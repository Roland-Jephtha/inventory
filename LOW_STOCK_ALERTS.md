# Low Stock Alert System

## Overview
The low stock alert system automatically monitors product inventory levels and sends email notifications when stock falls below the configured threshold.

## Features

✅ **Automatic Threshold Monitoring**
- Each product has a `low_stock_threshold` field (default: 5 units)
- When stock quantity ≤ threshold, alerts are triggered

✅ **Daily Email Reminders**
- First alert sent immediately when threshold is breached
- Subsequent reminders sent every 24 hours until stock is replenished
- Alert count tracked to show how many reminders have been sent

✅ **Smart Alert Management**
- Alerts automatically deactivate when stock is replenished above threshold
- No duplicate emails within 24-hour windows
- Email recipients: superusers with email addresses, or configured admin email

✅ **Real-time Trigger**
- Alerts fire immediately when:
  - Products are edited in the admin
  - Stock decreases due to sales
  - Stock is manually updated

## Setup

### 1. Configure Email Recipients

In `settings.py`, you can optionally set a specific email for alerts:

```python
# Option 1: Specific alert email
STOCK_ALERT_EMAIL = 'warehouse@mystore.com'

# Option 2: Multiple recipients
STOCK_ALERT_EMAIL = ['warehouse@mystore.com', 'manager@mystore.com']
```

If not configured, emails are sent to all superusers with email addresses.

### 2. Set Low Stock Thresholds

In Django Admin → Products:
- Edit each product
- Set `Low Stock Threshold` (e.g., 5 units)
- Save

### 3. Run Daily Alert Check

To send daily reminder emails, set up a cron job or task scheduler:

```bash
# Run every day at 9 AM
0 9 * * * cd /path/to/project && python manage.py check_stock_alerts
```

**For development**, you can run manually:
```bash
python manage.py check_stock_alerts
```

## Database Schema

### LowStockAlert Model
```python
- product (ForeignKey to Product)
- last_alert_sent (DateTime - auto-updated)
- reminder_count (Integer - tracks number of reminders)
- is_active (Boolean - alert is relevant)
```

## How It Works

### When Stock Falls Below Threshold:
1. Signal fires when product is saved
2. LowStockAlert record is created (if first time)
3. Email sent to configured recipients
4. `reminder_count` incremented
5. `last_alert_sent` timestamp updated

### When Stock is Replenished:
1. Product stock quantity increased
2. Signal checks if stock > threshold
3. LowStockAlert.is_active set to False
4. No more emails sent for this product

### Daily Cron Job:
1. Finds all products with stock ≤ threshold
2. Checks LowStockAlert records
3. Sends reminders if 24+ hours since last alert
4. Updates reminder count and timestamp

## Email Example

```
Subject: ⚠️ LOW STOCK ALERT: Product Name - My Store

Hello,

We're writing to inform you that the following product is running low on stock:

Product: Product Name
Current Stock: 3 units
Low Stock Threshold: 5 units
Stock Alert #2

Please arrange to restock this item as soon as possible.

Store: My Store
Alert Time: 2024-12-11 14:30:00
```

## Admin Interface

View all stock alerts in Django Admin → Low Stock Alerts:
- **List Display**: Product name, last alert sent, reminder count, is_active
- **Filters**: By active status, by date range
- **Search**: By product name

## API/Views

You can check programmatically:

```python
from store.models import LowStockAlert, Product

# Get all active alerts
active_alerts = LowStockAlert.objects.filter(is_active=True)

# Check if a product has low stock
product = Product.objects.get(id=1)
try:
    alert = LowStockAlert.objects.get(product=product)
    print(f"Alert active: {alert.is_active}")
    print(f"Reminders sent: {alert.reminder_count}")
except LowStockAlert.DoesNotExist:
    print("No alert for this product")
```

## Management Command

```bash
# Check and send low stock alerts
python manage.py check_stock_alerts

# Output examples:
# ✓ Sent low stock alert for Product A
# ✓ Deactivated alert for Product B - stock replenished
# 📧 Sent 2 low stock alert(s)
```

## Troubleshooting

### Emails Not Sending
1. Check email configuration in settings.py
2. Verify `DEFAULT_FROM_EMAIL` is set
3. Check console for error messages
4. Ensure superusers have email addresses configured

### Alerts Not Triggering
1. Verify product `low_stock_threshold` > 0
2. Check if `LowStockAlert.is_active` is True
3. Run `python manage.py check_stock_alerts` manually
4. Check Django logs for errors

### Too Many Emails
1. Ensure 24-hour gap between reminders is being respected
2. Check `last_alert_sent` timestamp in admin
3. Manually deactivate alert if needed

## Future Enhancements
- SMS notifications
- Slack/Teams integration
- Dashboard widget showing all low stock items
- Automatic reorder suggestions
- Low stock reports/analytics
