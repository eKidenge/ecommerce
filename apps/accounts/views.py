from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, 
    AddressForm, VendorRegistrationForm, ChangePasswordForm,
    ForgotPasswordForm, ResetPasswordForm
)
from .models import User, Address, UserActivityLog
import logging

logger = logging.getLogger(__name__)

def log_user_activity(user, action, description, request):
    """Helper function to log user activities"""
    try:
        UserActivityLog.objects.create(
            user=user,
            action=action,
            description=description,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")

def send_verification_email(user, request):
    """Send email verification link"""
    verification_url = request.build_absolute_uri(
        f'/accounts/verify-email/{user.verification_token}/'
    )
    subject = 'Verify Your Email Address'
    message = f"""
    Hello {user.full_name},
    
    Thank you for registering with E-Store. Please click the link below to verify your email address:
    
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you did not register for an account, please ignore this email.
    
    Best regards,
    E-Store Team
    """
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")

@csrf_protect
@cache_control(no_cache=True, must_revalidate=True)
def register(request):
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                log_user_activity(user, 'registration', 'User registered', request)
                send_verification_email(user, request)
                login(request, user)
                messages.success(request, 'Registration successful! Please check your email to verify your account.')
                return redirect('products:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@csrf_protect
@cache_control(no_cache=True, must_revalidate=True)
def user_login(request):
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.locked_until and user.locked_until > timezone.now():
                    messages.error(request, f'Account locked. Try again after {user.locked_until.strftime("%H:%M")}')
                    return render(request, 'accounts/login.html', {'form': form})
                
                login(request, user)
                user.failed_login_attempts = 0
                user.last_login_ip = request.META.get('REMOTE_ADDR')
                user.save()
                log_user_activity(user, 'login', 'User logged in', request)
                
                messages.success(request, f'Welcome back, {user.full_name}!')
                
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('products:home')
            else:
                try:
                    user = User.objects.get(username=username)
                    user.failed_login_attempts += 1
                    if user.failed_login_attempts >= 5:
                        user.lock_account()
                        messages.error(request, 'Account locked due to multiple failed login attempts. Please try again after 30 minutes.')
                    else:
                        remaining = 5 - user.failed_login_attempts
                        messages.error(request, f'Invalid credentials. {remaining} attempts remaining.')
                    user.save()
                except User.DoesNotExist:
                    messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    log_user_activity(request.user, 'logout', 'User logged out', request)
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('products:home')

@login_required
def profile(request):
    user = request.user
    addresses = user.addresses.filter(is_active=True)
    orders = user.orders.all().order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'addresses': addresses,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_user_activity(request.user, 'profile_update', 'Updated profile', request)
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password1 = form.cleaned_data.get('new_password1')
            
            if not request.user.check_password(old_password):
                messages.error(request, 'Current password is incorrect.')
            else:
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                log_user_activity(request.user, 'password_change', 'Changed password', request)
                messages.success(request, 'Password changed successfully!')
                return redirect('accounts:profile')
    else:
        form = ChangePasswordForm()
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def verify_email(request):
    if request.user.is_email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        send_verification_email(request.user, request)
        messages.success(request, 'Verification email sent! Please check your inbox.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/verify_email.html')

def verify_email_token(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Email verified successfully!')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
    
    return redirect('accounts:login')

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                reset_token = user.generate_reset_token()
                reset_url = request.build_absolute_uri(f'/accounts/reset-password/{reset_token}/')
                send_mail(
                    'Password Reset - E-Store',
                    f'Hello {user.full_name},\n\nClick the link to reset your password:\n{reset_url}\n\nThis link will expire in 24 hours.\n\nIf you did not request this, please ignore this email.',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=True,
                )
                messages.success(request, 'Password reset link sent to your email.')
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})

def reset_password(request, token):
    try:
        user = User.objects.get(reset_token=token, reset_token_expires__gt=timezone.now())
        
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data.get('new_password')
                user.set_password(new_password)
                user.reset_token = None
                user.reset_token_expires = None
                user.save()
                messages.success(request, 'Password reset successfully! Please login.')
                return redirect('accounts:login')
        else:
            form = ResetPasswordForm()
        
        return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired reset token.')
        return redirect('accounts:forgot_password')

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            log_user_activity(request.user, 'profile_update', 'Added new address', request)
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:profile')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/add_address.html', {'form': form})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            log_user_activity(request.user, 'profile_update', 'Updated address', request)
            messages.success(request, 'Address updated successfully!')
            return redirect('accounts:profile')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/edit_address.html', {'form': form, 'address': address})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        log_user_activity(request.user, 'profile_update', 'Deleted address', request)
        messages.success(request, 'Address deleted successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/delete_address.html', {'address': address})

@login_required
def vendor_registration(request):
    """View for vendors to register their store"""
    if request.user.is_vendor:
        messages.info(request, 'You are already registered as a vendor.')
        return redirect('dashboard:vendor_dashboard')
    
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            log_user_activity(request.user, 'profile_update', 'Registered as vendor', request)
            messages.success(request, 'Vendor registration successful! Your store is now active.')
            return redirect('dashboard:vendor_dashboard')
    else:
        form = VendorRegistrationForm(instance=request.user)
    
    return render(request, 'accounts/vendor_registration.html', {'form': form})

@login_required
def delete_account(request):
    """View for users to delete their account"""
    if request.method == 'POST':
        user = request.user
        # Log the activity before deleting
        log_user_activity(user, 'profile_update', 'Deleted account', request)
        # Delete the user
        user.delete()
        logout(request)
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('products:home')
    
    return render(request, 'accounts/delete_account.html')

@login_required
def resend_verification(request):
    """Resend email verification link"""
    if request.user.is_email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('accounts:profile')
    
    send_verification_email(request.user, request)
    messages.success(request, 'Verification email resent! Please check your inbox.')
    return redirect('accounts:profile')

def check_username(request):
    """AJAX view to check if username is available"""
    username = request.GET.get('username', '')
    if username:
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'available': not exists})
    return JsonResponse({'available': False})

def check_email(request):
    """AJAX view to check if email is available"""
    email = request.GET.get('email', '')
    if email:
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'available': not exists})
    return JsonResponse({'available': False})