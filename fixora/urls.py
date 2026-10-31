"""
URL configuration for fixora project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('services/', include('services.urls', namespace='services')),
    path('providers/', include('providers.urls', namespace='providers')),
    path('availability/', include('availability.urls', namespace='availability')),
    path('estimates/', include('estimates.urls', namespace='estimates')),
    path('', include('discovery.urls', namespace='discovery')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
