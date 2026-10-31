from django.contrib import admin
from .models import EstimateRequest, EstimateResponse


@admin.register(EstimateRequest)
class EstimateRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'provider', 'service_category', 'status', 'created_at')
    list_filter = ('status', 'service_category', 'created_at')
    search_fields = ('title', 'description', 'customer__email', 'provider__business_name')


@admin.register(EstimateResponse)
class EstimateResponseAdmin(admin.ModelAdmin):
    list_display = ('request', 'estimated_price', 'valid_until', 'responded_at')
    search_fields = ('request__title', 'explanation')
