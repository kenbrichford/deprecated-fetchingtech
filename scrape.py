import os
import hmac
import hashlib
import base64
import time
from urllib import request
from urllib.parse import urlunparse, quote_plus
from datetime import datetime, timedelta
from decimal import Decimal
import xmltodict
import django
from django.utils import timezone
from django.db.models import Q

class AmazonListing:
    """
    This class provides functionality for parsing and uploading information
    from Amazon's Product API.

    Attributes:
        listing (Listing Object): Listing item stored in the database
    """
    def __init__(self, amazon_listing):
        """
        Constructor for the AmazonListing class.

        Parameters:
            listing (Listing Object): Listing item pulled from the database
        """
        self.amazon_listing = amazon_listing

    def start_parse(self):
        """
        Initiate the parsing of information from Amazon.
        """
        url = self.create_amazon_url()
        response = parse_xml(url)['ItemLookupResponse']['Items']
        self.check_errors(response)

    def create_amazon_url(self):
        """
        Create an Amazon API URL with query parameters and authorization signature.

        Returns:
            string: Amazon API URL string
        """
        access_key = os.environ['AWS_ACCESS_KEY_ID']
        secret_key = os.environ['AWS_SECRET_ACCESS_KEY'].encode()
        assoc_tag = os.environ['AMAZON_ASSOCIATE_TAG']

        query = sorted([
            'Service=AWSECommerceService', 'Operation=ItemLookup',
            'AWSAccessKeyId='+access_key, 'AssociateTag='+assoc_tag,
            'ItemId='+self.amazon_listing.identifier, 'IdType=ASIN', 'Condition=All',
            'ResponseGroup=Images%2CItemAttributes%2COfferFull%2CSalesRank',
            'Timestamp='+datetime.utcnow().strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ')
        ])
        message = 'GET\nwebservices.amazon.com\n/onca/xml\n'+'&'.join(query)
        signature = base64.b64encode(
            hmac.new(
                secret_key,
                msg=message.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
        ).decode()
        query.append('Signature='+quote_plus(signature))
        url_tuple = (
            'http', 'webservices.amazon.com', '/onca/xml', '',
            '&'.join(query), ''
        )
        url = urlunparse(url_tuple)

        return url

    def check_errors(self, response):
        """
        Check for errors in item response, and move on to conditions if none.

        Parameters:
            response (dictionary): Dict containing listing and error info.
        """
        if not 'Errors' in response['Request']:
            item = response['Item']
            self.loop_through_conditions(item)
        else:
            error_code = response['Request']['Errors']['Error']['Code']
            if error_code == 'AWS.ECommerceService.ItemNotAccessible':
                self.amazon_listing.delete()

    def loop_through_conditions(self, item):
        """
        Check if the listing has a preassigned condition type. If not, check all
        three condition types for offers. Call parse function on each condition
        and on the product variant.

        Parameters:
            item (dictionary): Dict containing data specific to the listing.
        """
        self.extract_variant(item)
        if not self.amazon_listing.condition:
            conditions = (
                ('new', 'New'), ('used', 'Used'), ('refurb', 'Refurbished')
            )
            for condition in conditions:
                if 'Offer' in item['Offers']:
                    if isinstance(item['Offers']['Offer'], list):
                        offers = item['Offers']['Offer']
                    else:
                        offers = [item['Offers']['Offer']]
                    offer = next(
                        (
                            x for x in offers if x['OfferAttributes']['Condition'] == condition[1]
                        ), None
                    )
                else:
                    offer = None
                self.extract_pricing(item, offer, condition[0])
        else:
            if 'Offer' in item['Offers']:
                if isinstance(item['Offers']['Offer'], list):
                    offer = item['Offers']['Offer'][0]
                else:
                    offer = item['Offers']['Offer']
            else:
                offer = None
            self.extract_pricing(item, offer, self.amazon_listing.condition)

    def extract_variant(self, item):
        """
        Pull up-to-date information about the product variant from Amazon. Then
        call the update to send data to the database.

        Parameters:
            item (dictionary): Item response data
        """
        if 'LargeImage' in item:
            image = item['LargeImage']['URL']
        elif 'ImageSets' in item:
            if isinstance(item['ImageSets']['ImageSet'], list):
                image = item['ImageSets']['ImageSet'][0]['LargeImage']['URL']
            else:
                image = item['ImageSets']['ImageSet']['LargeImage']['URL']
        else:
            image = None
        rank = int(item['SalesRank']) if 'SalesRank' in item else None

        attr = item['ItemAttributes']
        upc = attr['UPC'] if 'UPC' in attr else ''
        ean = attr['EAN'] if 'EAN' in attr else ''
        msrp = Decimal(attr['ListPrice']['Amount'])/100 if 'ListPrice' in attr else None
        variant_info = {
            'image': image, 'rank': rank, 'upc': upc, 'ean': ean, 'msrp': msrp
        }

        self.upload_variant(variant_info)

    def update_variant(self, variant_info):
        """
        Send updated variant information to the database.

        Parameters:
            variant_info (dictionary): Collection of variant related information.
        """
        variant = Variant.objects.get(pk=self.amazon_listing.variant_id)
        variant.rank = variant_info['rank']
        variant.msrp = variant_info['msrp']

        variant.image = variant_info['image'] if not variant.image else variant.image
        variant.upc = variant_info['upc'] if not variant.upc else variant.upc
        variant.ean = variant_info['ean'] if not variant.ean else variant.ean

        variant.save()

    def extract_pricing(self, item, offer, condition):
        """
        Create a user product url and retrieve any necessary pricing information
        from the item response. Then, call the upload data function.

        Parameters:
            item (dictionary): Item response data
            offer (dictionary): Item offer information
            condition (string): The items condition as a string
        """
        url = item['Offers']['MoreOffersUrl']
        if not self.amazon_listing.condition:
            if condition == 'new':
                url += '&f_new=True'
            elif condition == 'used':
                url += """
                    &f_used=true&f_usedAcceptable=true&f_usedGood=true
                    &f_usedLikeNew=true&f_usedVeryGood=true
                """
            elif condition == 'refurb':
                url += '&f_refurbished=true'

        if offer:
            if 'SalePrice' in offer['OfferListing']:
                price_data = offer['OfferListing']['SalePrice']
            else:
                price_data = offer['OfferListing']['Price']
            price = Decimal(price_data['Amount'])/100 if 'Amount' in price_data else None
            currency = price_data['CurrencyCode'] if 'Amount' in price_data else ''
            shipping_type = 'prime' if offer['OfferListing']['IsEligibleForPrime'] == '1' else ''
            seller = offer['Merchant']['Name']
        else:
            price = None
            currency = shipping_type = seller = ''
        pricing_info = {
            'url': url, 'condition': condition, 'price': price,
            'currency': currency, 'total': price, 'shipping': None,
            'shipping_type': shipping_type, 'seller': seller, 'rating': ''
        }

        self.upload_pricing(pricing_info)

    def upload_pricing(self, pricing_info):
        """
        Upload the parsed pricing information to the database.

        Parameters:
            pricing_info (dictionary): Collection of listing data items.
        """
        current = Price.objects.filter(
            listing=self.amazon_listing,
            condition=pricing_info['condition'],
            is_current=True
        ).order_by('-time').first()
        previous = Price.objects.filter(
            listing=self.amazon_listing,
            condition=pricing_info['condition'],
            is_current=False
        ).order_by('-time').first()
        if (current and previous and current.total == previous.total == pricing_info['total'] and
                current.currency == previous.currency == pricing_info['currency']):
            values = {
                'url': pricing_info['url'],
                'price': pricing_info['price'],
                'shipping': pricing_info['shipping'],
                'shipping_type': pricing_info['shipping_type'],
                'seller': pricing_info['seller'],
                'rating': pricing_info['rating']
            }
            for (key, value) in values.items():
                setattr(current, key, value)
            current.save()
        else:
            Price.objects.create(
                listing=self.amazon_listing,
                url=pricing_info['url'],
                condition=pricing_info['condition'],
                price=pricing_info['price'],
                currency=pricing_info['currency'],
                total=pricing_info['total'],
                shipping=pricing_info['shipping'],
                shipping_type=pricing_info['shipping_type'],
                seller=pricing_info['seller'],
                rating=pricing_info['rating']
            )
        self.amazon_listing.new = False
        self.amazon_listing.save()

def fetch_listings(retailer):
    """
    Retrieve next 60 listings from the database, oldest updates first.

    Parameters:
        retailer (string): Name of retailer whose listings should be returned.

    Returns:
        QuerySet: List of Listing objects.
    """
    listings = Listing.objects.filter(
        Q(retailer=retailer),
        Q(time__lte=timezone.now()-timedelta(hours=3)) | Q(new=True)
    ).order_by('time')[:60]
    return listings

def parse_xml(url):
    """
    Call URL creation function, parse XML data, and return data as a dictionary.

    Returns:
        dictionary: Data parsed from URL
    """
    with request.urlopen(url) as response:
        data = response.read()
    response = xmltodict.parse(data)
    return response

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ft.settings.prod')
    django.setup()

    from pricing.models import Listing, Price
    from products.models import Variant

    # Iterate through listings in the database and call the parse function. Pause
    # between runs to avoid hitting servers too often.
    for each_listing in fetch_listings('amazon'):
        start = timezone.now()
        AmazonListing(each_listing).start_parse()
        finish = timezone.now()
        duration = (finish - start).total_seconds()
        if duration < 9:
            time.sleep(9 - duration)
