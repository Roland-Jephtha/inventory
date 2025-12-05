from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pos/', views.pos, name='pos'),
    path('pos/add/', views.add_to_cart, name='add_to_cart'),
    path('pos/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('pos/decrement/<int:pk>/', views.decrement_from_cart, name='decrement_from_cart'),
    path('pos/checkout/', views.checkout, name='checkout'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/search/', views.search_customers, name='search_customers'),
    path('reports/', views.sales_report, name='sales_report'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/receipt/', views.sale_receipt, name='sale_receipt'),
    path('settings/', views.settings_view, name='settings'),
]
