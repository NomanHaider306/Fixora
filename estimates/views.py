from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import EstimateRequest, EstimateResponse
from .forms import EstimateRequestForm, EstimateResponseForm
from providers.models import ProviderProfile


@login_required
def estimate_request_create(request, provider_id):
    """
    US24 - Customer requests a preliminary price estimate from a provider.
    """
    if not request.user.is_customer and not request.user.is_administrator:
        messages.error(request, "Only customers can request price estimates.")
        return redirect('accounts:dashboard_redirect')

    provider = get_object_or_404(ProviderProfile, pk=provider_id)

    if request.method == 'POST':
        form = EstimateRequestForm(request.POST, provider=provider)
        if form.is_valid():
            est_request = form.save(commit=False)
            est_request.customer = request.user
            est_request.provider = provider
            est_request.save()
            messages.success(request, f"Your estimate request has been sent to {provider.display_name}!")
            return redirect('estimates:customer_list')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = EstimateRequestForm(provider=provider)

    return render(request, 'estimates/request_create.html', {
        'form': form,
        'provider': provider,
    })


@login_required
def customer_estimates_list(request):
    """
    US24 - Customer views all submitted estimate requests and their responses.
    """
    if not request.user.is_customer and not request.user.is_administrator:
        messages.error(request, "Access restricted to customers.")
        return redirect('accounts:dashboard_redirect')

    status_filter = request.GET.get('status', '').strip()
    estimates = EstimateRequest.objects.filter(customer=request.user).select_related('provider', 'service_category', 'response').order_by('-created_at')

    if status_filter in ['pending', 'responded', 'cancelled']:
        estimates = estimates.filter(status=status_filter)

    return render(request, 'estimates/customer_list.html', {
        'estimates': estimates,
        'status_filter': status_filter,
    })


@login_required
def provider_estimates_list(request):
    """
    US24 - Provider views all incoming estimate requests.
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Access restricted to service providers.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    status_filter = request.GET.get('status', '').strip()

    estimates = EstimateRequest.objects.filter(provider=profile).select_related('customer', 'service_category', 'response').order_by('-created_at')

    if status_filter in ['pending', 'responded', 'cancelled']:
        estimates = estimates.filter(status=status_filter)

    return render(request, 'estimates/provider_list.html', {
        'profile': profile,
        'estimates': estimates,
        'status_filter': status_filter,
    })


@login_required
def estimate_detail(request, pk):
    """
    US24 - View estimate details (accessible by the customer, the provider, or an admin).
    """
    estimate = get_object_or_404(
        EstimateRequest.objects.select_related('customer', 'provider', 'service_category', 'response'),
        pk=pk
    )

    # Permission check: customer, provider or admin
    is_customer = (estimate.customer == request.user)
    is_provider = (hasattr(request.user, 'provider_profile') and estimate.provider == request.user.provider_profile)

    if not (is_customer or is_provider or request.user.is_administrator):
        messages.error(request, "You are not authorized to view this estimate request.")
        return redirect('accounts:dashboard_redirect')

    response_form = None
    if is_provider and estimate.status == EstimateRequest.Status.PENDING:
        response_form = EstimateResponseForm()

    return render(request, 'estimates/detail.html', {
        'estimate': estimate,
        'is_customer': is_customer,
        'is_provider': is_provider,
        'response_form': response_form,
    })


@login_required
def estimate_respond(request, pk):
    """
    US24 - Service provider submits preliminary price estimate response.
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Only service providers can respond to estimate requests.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    estimate = get_object_or_404(EstimateRequest, pk=pk, provider=profile)

    if request.method == 'POST':
        form = EstimateResponseForm(request.POST)
        if form.is_valid():
            response_obj = form.save(commit=False)
            response_obj.request = estimate
            response_obj.save()

            estimate.status = EstimateRequest.Status.RESPONDED
            estimate.save()

            messages.success(request, f"Your estimate response for PKR {response_obj.estimated_price} has been sent to {estimate.customer.get_full_name() or estimate.customer.email}!")
            return redirect('estimates:detail', pk=estimate.pk)
        else:
            messages.error(request, "Please check the form for errors.")
            return redirect('estimates:detail', pk=estimate.pk)

    return redirect('estimates:detail', pk=estimate.pk)


@login_required
def estimate_request_cancel(request, pk):
    """
    US24 - Customer cancels an estimate request.
    """
    estimate = get_object_or_404(EstimateRequest, pk=pk, customer=request.user)
    if estimate.status != EstimateRequest.Status.PENDING:
        messages.warning(request, "Only pending requests can be cancelled.")
    else:
        estimate.status = EstimateRequest.Status.CANCELLED
        estimate.save()
        messages.info(request, "Estimate request cancelled.")

    return redirect('estimates:customer_list')
