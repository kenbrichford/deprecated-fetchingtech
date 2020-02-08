from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from pricing.admin import ListingInline

from .models import Category, Manufacturer, Product, Variant
from .forms import CategoryForm, ProductForm

class VariantInline(admin.StackedInline):
    model = Variant
    exclude = ('slug', 'ean', 'upc')
    extra = 1
    fk = 'product'
    show_change_link = True

class CategoryAdmin(MPTTModelAdmin):
    form = CategoryForm

class ManufacturerAdmin(admin.ModelAdmin):
    fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    model = Product
    form = ProductForm
    inlines = [VariantInline]
    search_fields = ('manufacturer__name', 'name')

class VariantAdmin(admin.ModelAdmin):
    model = Variant
    inlines = [ListingInline]
    exclude = ('slug', 'ean', 'upc')
    search_fields = ('product__manufacturer__name', 'product__name', 'name')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Variant, VariantAdmin)
