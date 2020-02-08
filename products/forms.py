from django import forms

from mptt.forms import TreeNodeChoiceField

from .models import Product, Category, Variant

class CategoryForm(forms.ModelForm):
    parent = TreeNodeChoiceField(
        queryset=Category.objects.all(), required=False
    )

    class Meta:
        model = Category
        exclude = ('slug',)

class ProductForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ('category', 'manufacturer', 'name')
