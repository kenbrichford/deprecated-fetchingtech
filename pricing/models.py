from django.db import models

from products.models import Variant

class Listing(models.Model):
    RETAILERS = (('amazon', 'Amazon'),)
    CONDITIONS = (('refurb', 'Refurbished'),)

    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    retailer = models.CharField(max_length=10, choices=RETAILERS)
    url = models.URLField(max_length=2000)
    condition = models.CharField(
        max_length=10, choices=CONDITIONS, blank=True, null=True
    )
    identifier = models.CharField(max_length=255, unique=True)
    new = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        condition = '(Refurbished)' if self.condition else ''
        return '%s %s %s %s' % (
            self.variant.product, self.variant.name, 'Amazon', condition
        )

    def save(self, *args, **kwargs):
        self.url = 'https://www.amazon.com/dp/%s?tag=fetchingtech-20' % (
            self.identifier
        )
        super(Listing, self).save(*args, **kwargs)

class Price(models.Model):
    CONDITIONS = (('new', 'New'), ('used', 'Used'), ('refurb', 'Refurbished'))
    SHIPPING = (('prime', 'Prime'),)
    CURRENCIES = (('USD', 'USD'),)

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    condition = models.CharField(max_length=10, choices=CONDITIONS)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    shipping = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00, null=True
    )
    shipping_type = models.CharField(max_length=10, blank=True, choices=SHIPPING)
    total = models.DecimalField(
        max_digits=9, decimal_places=2, blank=True, null=True
    )
    currency = models.CharField(max_length=3, default='USD', choices=CURRENCIES)
    seller = models.CharField(max_length=255, blank=True)
    time = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        Price.objects.filter(
            listing=self.listing, condition=self.condition, is_current=True
        ).exclude(pk=self.pk).update(is_current=False)
        self.total = self.price + self.shipping
        super(Price, self).save(*args, **kwargs)
