from django import forms

class ContactForm(forms.Form):
    SUBJECTS = (
        (None, '-- Subject --'), ('GENERAL', 'General'),
        ('LISTING ERROR', 'Listing Error'), ('SUGGESTION', 'Suggestion'),
        ('BUG REPORT', 'Bug Report'), ('OTHER', 'Other')
    )

    full_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Full name'}
        )
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email address'}
        )
    )
    subject = forms.ChoiceField(choices=SUBJECTS, required=True)
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'Message'}
        )
    )
