from django import forms

class PaymentForm(forms.Form):
    PAYMENT_METHODS = (
        ('stripe', 'Credit/Debit Card (Stripe)'),
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect,
        label='Select Payment Method'
    )
    
    # M-Pesa specific fields
    mpesa_phone = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '254712345678'
        }),
        label='M-Pesa Phone Number'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        mpesa_phone = cleaned_data.get('mpesa_phone')
        
        if payment_method == 'mpesa' and not mpesa_phone:
            self.add_error('mpesa_phone', 'Phone number is required for M-Pesa payments')
        
        return cleaned_data