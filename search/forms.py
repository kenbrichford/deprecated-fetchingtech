from django import forms

from mptt.forms import TreeNodeChoiceField

from products.models import Category

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=150, widget=forms.TextInput(
            attrs={
                'type': 'search', 'placeholder': 'Fetch the Future',
                'minlength': 3
            }
        )
    )
    category = TreeNodeChoiceField(
        queryset=Category.objects.filter(parent=None),
        empty_label='All Categories', required=False, to_field_name='slug'
    )
