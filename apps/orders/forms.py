from django import forms
from apps.accounts.models import Address

class CheckoutForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            addresses = user.addresses.filter(is_active=True)
            shipping_choices = [(addr.id, str(addr)) for addr in addresses]
            self.fields['shipping_address'].choices = shipping_choices
            self.fields['billing_address'].choices = [('', 'Same as shipping')] + shipping_choices
    
    shipping_address = forms.ChoiceField(
        widget=forms.RadioSelect,
        label='Shipping Address'
    )
    billing_address = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect,
        label='Billing Address'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Order notes (optional)'
        }),
        label='Order Notes'
    )
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the Terms and Conditions'
    )