from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('onboarding/business-setup/', views.business_setup, name='business_setup'),
]
