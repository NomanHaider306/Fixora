from django.urls import path
from . import views

app_name = 'availability'

urlpatterns = [
    # US15 - Weekly Working Hours
    path('schedule/', views.weekly_schedule_manage, name='weekly_schedule_manage'),
    # US16 - Block Dates and Online/Offline Toggle
    path('blocked-dates/', views.blocked_dates_manage, name='blocked_dates_manage'),
    path('blocked-dates/<int:pk>/delete/', views.blocked_date_delete, name='blocked_date_delete'),
    path('toggle-online/', views.toggle_online_status, name='toggle_online_status'),
    # US17 - Customer Availability Slots API / View
    path('slots/<int:provider_id>/', views.get_available_slots, name='get_available_slots'),
    path('calendar/<int:provider_id>/', views.provider_calendar_view, name='provider_calendar'),
]

