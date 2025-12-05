from django.contrib import admin
from .models import Product, Category, SaleItem, Sale, Customer, Expense, StoreSettings

# Register your models here.





admin.site.register(Product)
admin.site.register(Category)
admin.site.register(SaleItem)
admin.site.register(Sale)
admin.site.register(Customer)
admin.site.register(Expense)
admin.site.register(StoreSettings)

