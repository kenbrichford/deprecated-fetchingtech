import operator

from functools import reduce

from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Subquery, OuterRef, Q

from products.models import Product, Category, Variant

from pricing.models import Price

def search(request):
    query = request.GET.get('query', None)
    category = request.GET.get('category', None)
    page = request.GET.get('page', 1)

    image = Variant.objects.filter(product_id=OuterRef('pk'))
    new = Price.objects.filter(
        listing__variant__product=OuterRef('pk'), is_current=True,
        condition='new'
    ).order_by('total')
    used = Price.objects.filter(
        listing__variant__product=OuterRef('pk'), s_current=True,
        condition='used'
    ).order_by('total')
    refurb = Price.objects.filter(
        listing__variant__product=OuterRef('pk'), is_current=True,
        condition='refurb'
    ).order_by('total')

    if query:
        q = reduce(operator.and_, (Q(search__icontains=x) for x in query.split()))
        products = Product.objects.filter(q).annotate(
            image=Subquery(image.values('image')[:1]),

            new_price=Subquery(new.values('price')[:1]),
            used_price=Subquery(used.values('price')[:1]),
            refurb_price=Subquery(refurb.values('price')[:1]),

            new_shipping=Subquery(new.values('shipping_type')[:1]),
            used_shipping=Subquery(used.values('shipping_type')[:1]),
            refurb_shipping=Subquery(refurb.values('shipping_type')[:1]),
        )

        if category:
            products = products.filter(
                category__in=Category.objects.get(
                    slug=category
                ).get_descendants(include_self=True)
            )

        count = products.count()
    else:
        products = Product.objects.none()
        count = None

    if category:
        categories = Category.objects.filter(slug=category)
    else:
        categories = Category.objects.filter(parent=None)

    paginator = Paginator(products, 50)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'products': products, 'count': count, 'categories': categories,
    })
