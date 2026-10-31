from django.urls import path
from . import views

app_name = 'discovery'

urlpatterns = [
    # Homepage
    path('', views.home_view, name='home'),
    # US11 - Browse Services
    path('explore/', views.explore_services_view, name='explore'),
    path('category/<slug:slug>/', views.category_providers_view, name='category_providers'),
    # US12 & US13 - Search, Filter, Sort
    path('search/', views.search_providers_view, name='search'),
    # US14 - Customer Favourites
    path('favourites/', views.favourites_list_view, name='favourites_list'),
    path('favourites/toggle/<int:provider_id>/', views.toggle_favourite_view, name='toggle_favourite'),
]

