from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q, Count
from services.models import ServiceCategory
from providers.models import ProviderProfile
from .models import Favourite


def home_view(request):
    """
    Marketplace Homepage inspired by Thumbtack.
    Shows hero search, popular categories, top-rated providers, how it works, and CTA.
    """
    categories = ServiceCategory.objects.filter(is_active=True).annotate(
        active_provider_count=Count('providers')
    )[:8]

    featured_providers = ProviderProfile.objects.filter(
        is_online=True
    ).select_related('user').prefetch_related('categories')[:6]

    # Favourite ids for current logged-in customer
    user_fav_ids = set()
    if request.user.is_authenticated and request.user.is_customer:
        user_fav_ids = set(Favourite.objects.filter(customer=request.user).values_list('provider_id', flat=True))

    context = {
        'categories': categories,
        'featured_providers': featured_providers,
        'user_fav_ids': user_fav_ids,
    }
    return render(request, 'discovery/home.html', context)


def explore_services_view(request):
    """
    US11 - Browse Services by Category
    Dedicated page displaying all service categories with live provider counts.
    """
    categories = ServiceCategory.objects.filter(is_active=True).annotate(
        provider_count=Count('providers')
    ).order_by('name')

    return render(request, 'discovery/explore.html', {'categories': categories})


def category_providers_view(request, slug):
    """
    US11 - Display providers associated with selected category.
    Supports filtering and sorting.
    """
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    providers = ProviderProfile.objects.filter(categories=category).select_related('user').prefetch_related('categories')

    return _filter_and_render_providers(request, providers, active_category=category)


def search_providers_view(request):
    """
    US12 & US13 - Location-Based Provider Search, Filtering, and Sorting.
    """
    providers = ProviderProfile.objects.all().select_related('user').prefetch_related('categories')
    return _filter_and_render_providers(request, providers)


def _filter_and_render_providers(request, queryset, active_category=None):
    """
    Helper function applying search parameters, filters, and sorting to providers queryset.
    """
    q = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    category_id = request.GET.get('category', '').strip()
    min_rating = request.GET.get('rating', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    availability = request.GET.get('availability', '').strip()
    sort_by = request.GET.get('sort', 'default').strip()

    # Search keyword filter (US12)
    if q:
        queryset = queryset.filter(
            Q(business_name__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(skills__icontains=q) |
            Q(introduction__icontains=q) |
            Q(categories__name__icontains=q)
        ).distinct()

    # Location filter (US12)
    if location:
        queryset = queryset.filter(
            Q(city__icontains=location) |
            Q(service_area__icontains=location)
        )

    # Category dropdown filter
    if category_id:
        try:
            queryset = queryset.filter(categories__id=int(category_id))
        except ValueError:
            pass

    # Rating filter (US13)
    if min_rating:
        try:
            rating_val = float(min_rating)
            queryset = queryset.filter(rating__gte=rating_val)
        except ValueError:
            pass

    # Price range filter (US13)
    if min_price:
        try:
            min_p = float(min_price)
            queryset = queryset.filter(
                Q(starting_price__gte=min_p) | Q(hourly_rate__gte=min_p)
            )
        except ValueError:
            pass

    if max_price:
        try:
            max_p = float(max_price)
            queryset = queryset.filter(
                Q(starting_price__lte=max_p) | Q(hourly_rate__lte=max_p)
            )
        except ValueError:
            pass

    # Availability filter (US13)
    if availability == 'online':
        queryset = queryset.filter(is_online=True)

    # Sorting options (US13)
    if sort_by == 'rating_desc':
        queryset = queryset.order_by('-rating', '-review_count')
    elif sort_by == 'price_asc':
        queryset = queryset.order_by('starting_price', 'hourly_rate')
    elif sort_by == 'price_desc':
        queryset = queryset.order_by('-starting_price', '-hourly_rate')
    elif sort_by == 'availability':
        queryset = queryset.order_by('-is_online', '-rating')
    else:
        queryset = queryset.order_by('-rating', '-created_at')

    # Favourites set
    user_fav_ids = set()
    if request.user.is_authenticated and request.user.is_customer:
        user_fav_ids = set(Favourite.objects.filter(customer=request.user).values_list('provider_id', flat=True))

    all_categories = ServiceCategory.objects.filter(is_active=True).order_by('name')

    context = {
        'providers': queryset,
        'all_categories': all_categories,
        'active_category': active_category,
        'user_fav_ids': user_fav_ids,
        'q': q,
        'location': location,
        'selected_category': category_id,
        'min_rating': min_rating,
        'min_price': min_price,
        'max_price': max_price,
        'availability': availability,
        'sort_by': sort_by,
        'results_count': queryset.count(),
    }
    return render(request, 'discovery/search_results.html', context)


@login_required
def toggle_favourite_view(request, provider_id):
    """
    US14 - Add or Remove Provider from Customer Favourites
    Supports both AJAX and standard form submissions.
    """
    if not request.user.is_customer and not request.user.is_administrator:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Only customers can favourite providers.'}, status=403)
        messages.error(request, "Only customers can save favourites.")
        return redirect('discovery:home')

    provider = get_object_or_404(ProviderProfile, pk=provider_id)
    fav_qs = Favourite.objects.filter(customer=request.user, provider=provider)

    is_fav = False
    if fav_qs.exists():
        fav_qs.delete()
        is_fav = False
        msg = f"{provider.display_name} removed from your favourites."
    else:
        Favourite.objects.create(customer=request.user, provider=provider)
        is_fav = True
        msg = f"{provider.display_name} added to your favourites!"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favourite': is_fav,
            'message': msg
        })

    messages.success(request, msg)
    next_url = request.META.get('HTTP_REFERER') or reverse('discovery:favourites_list')
    return redirect(next_url)


@login_required
def favourites_list_view(request):
    """
    US14 - Dedicated Customer Favourites Page
    """
    if not request.user.is_customer and not request.user.is_administrator:
        messages.error(request, "Access restricted to customers.")
        return redirect('accounts:dashboard_redirect')

    favourites = Favourite.objects.filter(
        customer=request.user
    ).select_related('provider', 'provider__user').prefetch_related('provider__categories')

    return render(request, 'discovery/favourites.html', {'favourites': favourites})
