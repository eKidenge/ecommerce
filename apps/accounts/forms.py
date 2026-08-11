from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User, Address

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678'
        })
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        initial='customer',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min 8 characters)'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    terms_agreement = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to our terms and conditions'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Vendor-specific fields (shown when vendor role is selected)
    store_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your store name'
        })
    )
    store_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe your store and what you sell'
        })
    )
    business_license = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Business license number'
        })
    )
    tax_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tax ID / KRA PIN'
        })
    )
    bank_account = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank account number'
        })
    )
    bank_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank name'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 
                  'user_type', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        # If user is registering as vendor, validate vendor fields
        if user_type == 'vendor':
            store_name = cleaned_data.get('store_name')
            if not store_name:
                self.add_error('store_name', 'Store name is required for vendors.')
            
            business_license = cleaned_data.get('business_license')
            if not business_license:
                self.add_error('business_license', 'Business license is required for vendors.')
            
            tax_id = cleaned_data.get('tax_id')
            if not tax_id:
                self.add_error('tax_id', 'Tax ID / KRA PIN is required for vendors.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.user_type = self.cleaned_data['user_type']
        
        # Save vendor-specific fields if user is a vendor
        if user.user_type == 'vendor':
            user.store_name = self.cleaned_data.get('store_name', '')
            user.store_description = self.cleaned_data.get('store_description', '')
            user.business_license = self.cleaned_data.get('business_license', '')
            user.tax_id = self.cleaned_data.get('tax_id', '')
            user.bank_account = self.cleaned_data.get('bank_account', '')
            user.bank_name = self.cleaned_data.get('bank_name', '')
        
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number',
                  'profile_picture', 'bio', 'address', 'city', 'state', 'country', 
                  'postal_code']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_type', 'address_line1', 'address_line2', 'city', 
                  'state', 'country', 'postal_code', 'phone_number', 'is_default']
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254712345678'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.startswith('+'):
            raise ValidationError('Phone number must start with +')
        return phone

class VendorProfileForm(forms.ModelForm):
    """Form for vendors to update their store information"""
    class Meta:
        model = User
        fields = ['store_name', 'store_description', 'store_logo', 'store_banner',
                  'business_license', 'tax_id', 'bank_account', 'bank_name', 
                  'is_store_active']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control'}),
            'store_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'store_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'store_banner': forms.FileInput(attrs={'class': 'form-control'}),
            'business_license': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_store_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError('Passwords do not match.')
        
        if new_password1 and len(new_password1) < 8:
            raise ValidationError('Password must be at least 8 characters.')
        
        return cleaned_data

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No user found with this email address.')
        return email

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError('Passwords do not match.')
        
        if new_password and len(new_password) < 8:
            raise ValidationError('Password must be at least 8 characters.')
        
        return cleaned_data

class VendorRegistrationForm(forms.ModelForm):
    """Standalone form for existing users to become vendors"""
    class Meta:
        model = User
        fields = ['store_name', 'store_description', 'business_license', 'tax_id',
                  'bank_account', 'bank_name']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control'}),
            'store_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'business_license': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'vendor'
        if commit:
            user.save()
        return user