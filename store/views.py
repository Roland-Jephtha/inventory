from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Sum
from django.utils import timezone
from .models import Product, Category, SaleItem, Sale, Customer
from .forms import ProductForm, CategoryForm, SaleForm, CustomerForm

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
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'store/product_confirm_delete.html', {'product': product})

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'store/customer_list.html', {'customers': customers, 'form': CustomerForm()})

@login_required
def sales_report(request):
    return render(request, 'store/sales_report.html')

@login_required
def settings_view(request):
    if request.method == 'POST':
        color = request.POST.get('theme_color')
        if color:
            request.session['theme_color'] = color
            messages.success(request, 'Theme updated.')
    return render(request, 'store/settings.html')

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
            messages.success(request, f'Sale completed. Total: ${total:.2f}')
            return redirect('dashboard')
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
