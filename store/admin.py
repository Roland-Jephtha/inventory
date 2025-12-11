from django.contrib import admin
from .models import Product, Category, SaleItem, Sale, Customer, Expense, StoreSettings, LowStockAlert

# Register your models here.

@admin.register(LowStockAlert)
class LowStockAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'last_alert_sent', 'reminder_count', 'is_active')
    list_filter = ('is_active', 'last_alert_sent')
    search_fields = ('product__name',)
    readonly_fields = ('last_alert_sent', 'reminder_count')

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(SaleItem)
admin.site.register(Sale)
admin.site.register(Customer)
admin.site.register(Expense)
admin.site.register(StoreSettings)
