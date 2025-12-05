from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('onboarding/business-setup/', views.business_setup, name='business_setup'),
    path('subscription/access-paused/', views.access_paused, name='access_paused'),
    path('subscription/verify/', views.verify_payment, name='verify_payment'),
]
