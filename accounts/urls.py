from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # US01 - Registration
    path('register/', views.register_view, name='register'),
    # US02 - Login
    path('login/', views.login_view, name='login'),
    # US03 - Logout
    path('logout/', views.logout_view, name='logout'),

    # Central Dispatcher
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # Role Dashboards
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/provider/', views.provider_dashboard, name='provider_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # US05 - Account Settings
    path('settings/', views.account_settings_view, name='account_settings'),

    # US04 - Password Reset Flow
    path('password-reset/', views.FixoraPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.FixoraPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.FixoraPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.FixoraPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

