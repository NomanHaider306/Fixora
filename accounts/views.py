from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    AccountSettingsForm,
    CustomerProfileForm
)
from .models import CustomerProfile

User = get_user_model()


def register_view(request):
    """
    US01 - User Registration
    Allows visitors to register as Customer or Service Provider.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log in automatically after registration
            login(request, user)
            messages.success(request, f"Welcome to Fixora, {user.first_name}! Your account has been created.")
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        role_param = request.GET.get('role', User.Role.CUSTOMER)
        initial_role = User.Role.PROVIDER if role_param == 'provider' else User.Role.CUSTOMER
        form = UserRegistrationForm(initial={'role': initial_role})

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    US02 - User Login
    Authenticates user and redirects to role-specific dashboard.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me')

            # Django authenticates by username; our username is set to email
            user = authenticate(request, username=email, password=password)
            if user is None:
                # Fallback check if user object has this email
                try:
                    user_obj = User.objects.get(email__iexact=email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                if user.is_active:
                    login(request, user)
                    if remember_me:
                        # 2 weeks session expiry
                        request.session.set_expiry(1209600)
                    else:
                        # Session closes with browser
                        request.session.set_expiry(0)

                    messages.success(request, f"Welcome back, {user.first_name or user.email}!")
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('accounts:dashboard_redirect')
                else:
                    messages.error(request, "This account has been deactivated. Please contact support.")
            else:
                messages.error(request, "Invalid email address or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    US03 - User Logout
    Terminates authenticated session and redirects to homepage.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out securely. Have a great day!")
    return redirect('discovery:home')


@login_required
def dashboard_redirect(request):
    """
    Central dispatcher redirecting user to their role-specific dashboard.
    """
    if request.user.is_administrator:
        return redirect('accounts:admin_dashboard')
    elif request.user.is_provider:
        return redirect('accounts:provider_dashboard')
    else:
        return redirect('accounts:customer_dashboard')


@login_required
def customer_dashboard(request):
    """
    Dashboard for Customers:
    Overview of estimate requests, favourite providers, and account status.
    """
    if not request.user.is_customer and not request.user.is_administrator:
        messages.warning(request, "Access restricted to customer accounts.")
        return redirect('accounts:dashboard_redirect')

    # Estimates requested by customer
    recent_estimates = request.user.estimate_requests.select_related('provider', 'service_category').order_by('-created_at')[:5]
    total_estimates_count = request.user.estimate_requests.count()
    pending_estimates_count = request.user.estimate_requests.filter(status='pending').count()
    responded_estimates_count = request.user.estimate_requests.filter(status='responded').count()
    favourites_count = request.user.favourite_providers.count()

    context = {
        'recent_estimates': recent_estimates,
        'total_estimates_count': total_estimates_count,
        'pending_estimates_count': pending_estimates_count,
        'responded_estimates_count': responded_estimates_count,
        'favourites_count': favourites_count,
    }
    return render(request, 'dashboards/customer_dashboard.html', context)


@login_required
def provider_dashboard(request):
    """
    Dashboard for Service Providers:
    Overview of received estimates, schedule status, online/offline status, portfolio.
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.warning(request, "Access restricted to service providers.")
        return redirect('accounts:dashboard_redirect')

    provider_profile = getattr(request.user, 'provider_profile', None)
    if not provider_profile:
        from providers.models import ProviderProfile
        provider_profile = ProviderProfile.objects.create(
            user=request.user,
            business_name=f"{request.user.get_full_name() or request.user.username} Services"
        )

    incoming_estimates = provider_profile.received_estimate_requests.select_related('customer', 'service_category').order_by('-created_at')[:5]
    pending_count = provider_profile.received_estimate_requests.filter(status='pending').count()
    responded_count = provider_profile.received_estimate_requests.filter(status='responded').count()
    portfolio_count = provider_profile.portfolio_images.count()
    documents_count = provider_profile.documents.count()

    context = {
        'profile': provider_profile,
        'incoming_estimates': incoming_estimates,
        'pending_count': pending_count,
        'responded_count': responded_count,
        'portfolio_count': portfolio_count,
        'documents_count': documents_count,
    }
    return render(request, 'dashboards/provider_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """
    Dashboard for Administrators:
    Platform overview, categories count, users count, estimates overview.
    """
    if not request.user.is_administrator:
        messages.error(request, "Administrator privileges required.")
        return redirect('accounts:dashboard_redirect')

    from services.models import ServiceCategory
    from providers.models import ProviderProfile, IdentityDocument
    from estimates.models import EstimateRequest

    total_users = User.objects.count()
    total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_providers = ProviderProfile.objects.count()
    total_categories = ServiceCategory.objects.count()
    total_estimates = EstimateRequest.objects.count()
    recent_providers = ProviderProfile.objects.select_related('user').order_by('-created_at')[:6]
    categories = ServiceCategory.objects.all().order_by('name')

    context = {
        'total_users': total_users,
        'total_customers': total_customers,
        'total_providers': total_providers,
        'total_categories': total_categories,
        'total_estimates': total_estimates,
        'recent_providers': recent_providers,
        'categories': categories,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def account_settings_view(request):
    """
    US05 - Account Details Update
    Allows authenticated users to update their personal details and contact info.
    """
    user = request.user
    customer_profile = getattr(user, 'customer_profile', None)

    if request.method == 'POST':
        account_form = AccountSettingsForm(request.POST, instance=user)
        profile_form = CustomerProfileForm(request.POST, instance=customer_profile) if customer_profile else None

        if account_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            account_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "Your account details have been updated successfully.")
            return redirect('accounts:account_settings')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        account_form = AccountSettingsForm(instance=user)
        profile_form = CustomerProfileForm(instance=customer_profile) if customer_profile else None

    context = {
        'account_form': account_form,
        'profile_form': profile_form,
        'user': user,
    }
    return render(request, 'accounts/settings.html', context)


# ==========================================
# US04 - Password Reset Views
# ==========================================
class FixoraPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class FixoraPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class FixoraPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class FixoraPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
