from django.urls import path
from . import views

app_name = 'providers'

urlpatterns = [
    # US06 & US07 - Profile Management & Category Selection
    path('profile/edit/', views.provider_profile_edit, name='profile_edit'),
    # US08 - Portfolio Photos
    path('portfolio/', views.portfolio_manage, name='portfolio_manage'),
    path('portfolio/<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),
    # US09 - Identity Document Submission
    path('documents/', views.document_submission, name='document_submission'),
    # US10 - Customer View of Provider Profile
    path('<int:pk>/', views.provider_public_profile, name='public_profile'),
]

