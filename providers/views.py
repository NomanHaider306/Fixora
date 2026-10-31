from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import ProviderProfile, PortfolioImage, IdentityDocument
from .forms import ProviderProfileForm, PortfolioImageForm, IdentityDocumentForm
from availability.models import WeeklySchedule, BlockedDate
from discovery.models import Favourite
from datetime import date


@login_required
def provider_profile_edit(request):
    """
    US06 & US07 - Provider Profile Creation and Category Selection
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Only service providers can access this page.")
        return redirect('accounts:dashboard_redirect')

    profile, created = ProviderProfile.objects.get_or_create(
        user=request.user,
        defaults={'business_name': f"{request.user.get_full_name() or request.user.username} Services"}
    )

    if request.method == 'POST':
        form = ProviderProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your professional profile has been updated successfully!")
            return redirect('providers:profile_edit')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = ProviderProfileForm(instance=profile)

    return render(request, 'providers/profile_edit.html', {
        'form': form,
        'profile': profile,
    })


@login_required
def portfolio_manage(request):
    """
    US08 - Provider Portfolio Photos
    Upload and manage gallery of previous projects.
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Only service providers can manage portfolio photos.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    photos = profile.portfolio_images.all()

    if request.method == 'POST':
        form = PortfolioImageForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio_item = form.save(commit=False)
            portfolio_item.provider = profile
            portfolio_item.save()
            messages.success(request, "Project photo added to your portfolio!")
            return redirect('providers:portfolio_manage')
        else:
            messages.error(request, "Failed to upload photo. Please check requirements.")
    else:
        form = PortfolioImageForm()

    return render(request, 'providers/portfolio_manage.html', {
        'profile': profile,
        'photos': photos,
        'form': form,
    })


@login_required
def portfolio_delete(request, pk):
    """
    US08 - Remove portfolio image
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Unauthorized.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    photo = get_object_or_404(PortfolioImage, pk=pk, provider=profile)

    if request.method == 'POST':
        photo.delete()
        messages.success(request, "Portfolio photo removed.")
    return redirect('providers:portfolio_manage')


@login_required
def document_submission(request):
    """
    US09 - Identity Document Submission
    Secure document submission for verification. Restricted from public exposure.
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Only service providers can submit identity documents.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    documents = profile.documents.all()

    if request.method == 'POST':
        form = IdentityDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.provider = profile
            doc.save()
            messages.success(request, "Identity document submitted for verification. Our admin team will review it.")
            return redirect('providers:document_submission')
        else:
            messages.error(request, "Failed to submit document. Please check the file format and size.")
    else:
        form = IdentityDocumentForm()

    return render(request, 'providers/document_submission.html', {
        'profile': profile,
        'documents': documents,
        'form': form,
    })


def provider_public_profile(request, pk):
    """
    US10 - Customer Provider Profile View
    Public profile display with bio, skills, categories, rates, portfolio,
    availability preview, and estimate request button.
    """
    provider = get_object_or_404(
        ProviderProfile.objects.select_related('user').prefetch_related('categories', 'portfolio_images'),
        pk=pk
    )

    # Check if favourite for current logged-in customer
    is_favourite = False
    if request.user.is_authenticated and request.user.is_customer:
        is_favourite = Favourite.objects.filter(customer=request.user, provider=provider).exists()

    # Weekly schedule for preview
    schedules = provider.weekly_schedules.all().order_by('day_of_week')
    schedule_map = {s.day_of_week: s for s in schedules}
    days_data = []
    for day_idx, day_name in WeeklySchedule.DAYS_OF_WEEK:
        sched = schedule_map.get(day_idx)
        days_data.append({
            'day_name': day_name,
            'is_working': sched.is_working if sched else False,
            'start_time': sched.start_time if sched and sched.is_working else None,
            'end_time': sched.end_time if sched and sched.is_working else None,
        })

    # Portfolio images
    portfolio_photos = provider.portfolio_images.all()

    context = {
        'provider': provider,
        'is_favourite': is_favourite,
        'days_data': days_data,
        'portfolio_photos': portfolio_photos,
        'today': date.today(),
    }
    return render(request, 'providers/public_profile.html', context)
