from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Sum
from django.utils import timezone
from .models import Product, Category, SaleItem, Sale, Customer, StoreSettings
from .forms import ProductForm, CategoryForm, SaleForm, CustomerForm
from users.decorators import owner_required

@login_required
def dashboard(request):
    today = timezone.now().date()
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock_quantity__lte=F('low_stock_threshold')).count()
    out_of_stock_count = Product.objects.filter(stock_quantity=0).count()
    sales_today = Sale.objects.filter(created_at__date=today).aggregate(total=Sum('total_amount'))['total'] or 0
    items_sold_today = SaleItem.objects.filter(sale__created_at__date=today).aggregate(total=Sum('quantity'))['total'] or 0
    low_items = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lte=F('low_stock_threshold')).order_by('stock_quantity')[:5]
    out_items = Product.objects.filter(stock_quantity=0).order_by('name')[:5]
    # Weekly revenue (Mon-Sun)
    start = today - timezone.timedelta(days=today.weekday())
    labels = []
    weekly = []
    for i in range(7):
        day = start + timezone.timedelta(days=i)
        labels.append(day.strftime('%a'))
        amt = Sale.objects.filter(created_at__date=day).aggregate(total=Sum('total_amount'))['total'] or 0
        weekly.append(float(amt))

    recent_sales = Sale.objects.order_by('-created_at')[:5]

    context = {
        'kpis': {
            'sales_today': sales_today,
            'total_products': total_products,
            'low_stock': low_stock_count,
            'out_of_stock': out_of_stock_count,
            'items_sold_today': items_sold_today,
        },
        'low_items': low_items,
        'out_items': out_items,
        'weekly_labels': labels,
        'weekly_data': weekly,
        'recent_sales': recent_sales,
    }
    return render(request, 'store/dashboard.html', context)

@login_required
def pos(request):
    # Initialize cart from session
    cart = request.session.get('cart', {})
    products = Product.objects.all().order_by('name')
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        try:
            prod = Product.objects.get(pk=pid)
            subtotal = prod.price * qty
            total += subtotal
            cart_items.append({
                'product': prod,
                'quantity': qty,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            continue
    context = {
        'products': products,
        'cart_items': cart_items,
        'cart_total': total,
        'sale_form': SaleForm(),
    }
    return render(request, 'store/pos.html', context)

@login_required
@owner_required
def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.all().select_related('category').order_by('-created_at')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(barcode__icontains=query) |
            Q(category__name__icontains=query)
        )
    context = {'products': products, 'search_query': query, 'form': ProductForm()}
    return render(request, 'store/product_list.html', context)

@login_required
@owner_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
@owner_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@owner_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'store/product_confirm_delete.html', {'product': product})

@login_required
def customer_list(request):
    customers = Customer.objects.annotate(
        total_spent=Sum('sales__total_amount')
    ).order_by('-created_at')
    return render(request, 'store/customer_list.html', {'customers': customers, 'form': CustomerForm()})

import csv
from django.http import HttpResponse

@login_required
def sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    sales = Sale.objects.select_related('customer').prefetch_related('items').order_by('-created_at')
    
    if start_date:
        sales = sales.filter(created_at__date__gte=start_date)
    if end_date:
        sales = sales.filter(created_at__date__lte=end_date)
    
    # Export to CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{timezone.now().date()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Reference', 'Customer', 'Payment Method', 'Items', 'Total Amount'])
        
        for sale in sales:
            writer.writerow([
                sale.created_at.strftime('%Y-%m-%d %H:%M'),
                sale.reference,
                sale.customer.name if sale.customer else 'Walk-in',
                sale.get_payment_method_display(),
                sale.items.count(),
                sale.total_amount
            ])
        
        # Add Total Row
        total_sum = sales.aggregate(total=Sum('total_amount'))['total'] or 0
        writer.writerow([])
        writer.writerow(['Total', '', '', '', '', total_sum])
        
        return response

    # Calculate KPIs
    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    sales_count = sales.count()
    items_sold = SaleItem.objects.filter(sale__in=sales).aggregate(total=Sum('quantity'))['total'] or 0
    average_sale = total_sales / sales_count if sales_count > 0 else 0
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'sales_count': sales_count,
        'items_sold': items_sold,
        'average_sale': average_sale,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'store/sales_report.html', context)

@login_required
@owner_required
def settings_view(request):
    # Get or create store settings
    store, created = StoreSettings.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        store.store_name = request.POST.get('store_name', store.store_name)
        store.address = request.POST.get('store_address', store.address)
        store.phone = request.POST.get('store_phone', store.phone)
        store.save()
        messages.success(request, 'Settings saved successfully!')
        return redirect('settings')
    
    return render(request, 'store/settings.html', {'store': store})

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + quantity
        request.session['cart'] = cart
        messages.success(request, 'Product added to cart.')
    return redirect('pos')

@login_required
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
        messages.info(request, 'Product removed from cart.')
    return redirect('pos')

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'Cart is empty.')
            return redirect('pos')
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.user = request.user
            
            # Handle Customer
            customer_id = request.POST.get('customer_id')
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            
            if customer_id:
                sale.customer_id = customer_id
            elif customer_name and customer_phone:
                customer, created = Customer.objects.get_or_create(
                    phone=customer_phone,
                    defaults={'name': customer_name}
                )
                sale.customer = customer
            
            sale.total_amount = 0
            sale.save()
            total = 0
            for pid, qty in cart.items():
                product = Product.objects.get(pk=pid)
                product.stock_quantity = max(product.stock_quantity - qty, 0)
                product.save()
                item = SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    price=product.price,
                )
                total += item.subtotal
            sale.total_amount = total
            sale.save()
            request.session['cart'] = {}
            messages.success(request, f'Sale completed! Reference: {sale.reference}')
            return redirect('sale_receipt', pk=sale.pk)
        else:
            messages.error(request, 'Please correct the errors in the form.')
    return redirect('pos')
@login_required
def decrement_from_cart(request, pk):
    cart = request.session.get('cart', {})
    key = str(pk)
    if key in cart:
        if cart[key] > 1:
            cart[key] -= 1
        else:
            del cart[key]
        request.session['cart'] = cart
        messages.info(request, 'Quantity updated.')
    return redirect('pos')
@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added.')
        else:
            messages.error(request, 'Please correct the errors.')
    return redirect('customer_list')

@login_required
def search_customers(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse([], safe=False)
    
    customers = Customer.objects.filter(
        Q(name__icontains=q) | Q(phone__icontains=q)
    )[:10]
    data = [{'id': c.id, 'name': c.name, 'phone': c.phone} for c in customers]
    return JsonResponse(data, safe=False)

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'user')
                    .prefetch_related('items__product'),
        pk=pk
    )
    return render(request, 'store/sale_detail.html', {'sale': sale})

@login_required
def sale_receipt(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'user')
                    .prefetch_related('items__product'),
        pk=pk
    )
    return render(request, 'store/sale_receipt.html', {'sale': sale})

