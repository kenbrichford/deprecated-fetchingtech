from django.contrib import admin

from .models import Listing, Price

class ListingInline(admin.TabularInline):
    model = Listing
    fields = ('retailer', 'condition', 'identifier')
    extra = 1
    fk_name = 'variant'
    show_change_link = True

class PriceInline(admin.TabularInline):
    model = Price
    exclude = ('total', 'time', 'is_current')
    extra = 1
    fk_name = 'listing'

class ListingAdmin(admin.ModelAdmin):
    model = Listing
    exclude = ('variant', 'retailer', 'condition', 'new', 'time')
    readonly_fields = ('url',)
    inlines = [PriceInline]
    search_fields = (
        'variant__product__manufacturer__name', 'variant__product__name',
        'variant__name'
    )

admin.site.register(Listing, ListingAdmin)
