from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('admin/categories/', views.category_list_admin, name='category_list_admin'),
    path('admin/categories/add/', views.category_create_admin, name='category_create_admin'),
    path('admin/categories/<int:pk>/edit/', views.category_update_admin, name='category_update_admin'),
    path('admin/categories/<int:pk>/toggle/', views.category_toggle_admin, name='category_toggle_admin'),
    path('admin/categories/<int:pk>/delete/', views.category_delete_admin, name='category_delete_admin'),
]

