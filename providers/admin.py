from django.contrib import admin
from .models import ProviderProfile, PortfolioImage, IdentityDocument


class PortfolioInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1


class IdentityDocumentInline(admin.TabularInline):
    model = IdentityDocument
    extra = 1


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'city', 'hourly_rate', 'is_online', 'is_verified', 'created_at')
    list_filter = ('is_online', 'is_verified', 'categories', 'city')
    search_fields = ('business_name', 'user__first_name', 'user__last_name', 'user__email', 'city', 'skills')
    inlines = [PortfolioInline, IdentityDocumentInline]


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ('provider', 'caption', 'uploaded_at')
    search_fields = ('provider__business_name', 'caption')


@admin.register(IdentityDocument)
class IdentityDocumentAdmin(admin.ModelAdmin):
    list_display = ('provider', 'document_type', 'status', 'submitted_at')
    list_filter = ('status', 'document_type')
    search_fields = ('provider__business_name', 'provider__user__email')
