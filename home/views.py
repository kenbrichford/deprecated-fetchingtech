from django.shortcuts import render
from django.db.models import Subquery, OuterRef

from products.models import Product

from pricing.models import Price, Variant

def home(request):
    image = Variant.objects.filter(product_id=OuterRef('pk'))

    new = Price.objects.filter(
        listing__variant__product_id=OuterRef('pk'),
        is_current=True, condition='new'
    ).order_by('total')
    used = Price.objects.filter(
        listing__variant__product_id=OuterRef('pk'),
        is_current=True, condition='used'
    ).order_by('total')
    refurb = Price.objects.filter(
        listing__variant__product_id=OuterRef('pk'),
        is_current=True, condition='refurb'
    ).order_by('total')

    products = Product.objects.order_by('rank')[:60].annotate(
        image=Subquery(image.values('image')[:1]),

        new_price=Subquery(new.values('price')[:1]),
        used_price=Subquery(used.values('price')[:1]),
        refurb_price=Subquery(refurb.values('price')[:1]),

        new_shipping=Subquery(new.values('shipping_type')[:1]),
        used_shipping=Subquery(used.values('shipping_type')[:1]),
        refurb_shipping=Subquery(refurb.values('shipping_type')[:1]),
    )
    return render(request, 'home/home.html', {'products': products})
