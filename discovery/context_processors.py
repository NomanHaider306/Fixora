def global_categories(request):
    """
    Context processor to make active categories available across all templates
    (e.g., in the navbar dropdown and footer).
    """
    try:
        from services.models import ServiceCategory
        categories = ServiceCategory.objects.filter(is_active=True)[:8]
    except Exception:
        categories = []
    return {'nav_categories': categories}

