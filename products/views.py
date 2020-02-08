import json

from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Subquery, OuterRef

from pricing.models import Price

from .models import Product, Category, Variant

def category_all(request):
    categories = Category.objects.filter(parent=None)
    return render(request, 'products/category_all.html', {
        'categories': categories
    })

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)

    image = Variant.objects.filter(product_id=OuterRef('pk'))
    new = Price.objects.filter(
        listing__variant__product=OuterRef('pk'), is_current=True,
        condition='new'
    ).order_by('total')
    used = Price.objects.filter(
        listing__variant__product=OuterRef('pk'), is_current=True,
        condition='used'
    ).order_by('total')
    refurb = Price.objects.filter(
        listing__variant__product=OuterRef('pk'), is_current=True,
        condition='refurb'
    ).order_by('total')

    products = Product.objects.filter(
        category__in=category.get_descendants(include_self=True)
    ).order_by('rank').annotate(
        image=Subquery(image.values('image')[:1]),

        new_price=Subquery(new.values('price')[:1]),
        used_price=Subquery(used.values('price')[:1]),
        refurb_price=Subquery(refurb.values('price')[:1]),

        new_shipping=Subquery(new.values('shipping_type')[:1]),
        used_shipping=Subquery(used.values('shipping_type')[:1]),
        refurb_shipping=Subquery(refurb.values('shipping_type')[:1]),
    )
    page = request.GET.get('page', 1)

    paginator = Paginator(products, 50)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/category.html', {
        'category': category, 'products': products
    })

def product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variants = Variant.objects.filter(product=product)
    variant_prices = Price.objects.filter(
        listing__variant__in=variants, is_current=True
    ).exclude(seller='').order_by('condition', 'total')
    return render(request, 'products/product.html', {
        'product': product, 'variants': variants,
        'variant_prices': variant_prices
    })

def variant(request, product, variant):
    variant = get_object_or_404(Variant, product__slug=product, slug=variant)
    current_prices = Price.objects.filter(
        listing__variant=variant, is_current=True
    ).exclude(seller='').order_by('condition', 'total')
    retailers = ('amazon',)
    conditions = ('new', 'refurb', 'used')
    colors = {'amazon': '18, 52, 86'}
    opacities = {'new': 1, 'refurb': .67, 'used': .33}
    all_prices = Price.objects.filter(listing__variant=variant).order_by('time')
    price_history = []
    for retailer in retailers:
        main_color = colors[retailer]
        for condition in conditions:
            opacity = opacities[condition]
            color = 'rgba(%s, %s)' % (main_color, opacity)
            label = '%s (%s)' % (retailer.title(), condition)
            data = [{
                'x': price.time.isoformat(),
                'y': float(price.total) if price.total else None
            } for price in all_prices.filter(
                listing__retailer=retailer, condition=condition
            )]
            price_history.append({
                'label': label, 'data': data, 'borderColor': color,
                'backgroundColor': color, 'fill': False, 'steppedLine': True
            })
    low_prices = []
    for condition in conditions:
        low_prices.append(
            all_prices.filter(condition=condition).exclude(
                total=None).order_by('total', '-time').first()
        )
    return render(request, 'products/variant.html', {
        'variant': variant, 'current_prices': current_prices, 'price_history':
        json.dumps(price_history), 'low_prices': low_prices
    })
