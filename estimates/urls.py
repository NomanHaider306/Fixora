from django.urls import path
from . import views

app_name = 'estimates'

urlpatterns = [
    # Customer flows (US24)
    path('request/<int:provider_id>/', views.estimate_request_create, name='request_create'),
    path('my-requests/', views.customer_estimates_list, name='customer_list'),
    path('request/<int:pk>/cancel/', views.estimate_request_cancel, name='request_cancel'),

    # Provider flows (US24)
    path('incoming/', views.provider_estimates_list, name='provider_list'),
    path('<int:pk>/respond/', views.estimate_respond, name='respond'),

    # Common detail view
    path('<int:pk>/', views.estimate_detail, name='detail'),
]

