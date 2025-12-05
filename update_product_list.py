content = r'''{% extends 'layouts/app.html' %}
{% load humanize %}

{% block title %}Products - POS-Lite{% endblock %}

{% block appbar_title %}Inventory{% endblock %}

{% block header_actions %}
<button onclick="openModal()" class="w-9 h-9 rounded-full bg-primary-600 text-white flex items-center justify-center shadow-lg shadow-primary-600/30">
    <i data-feather="plus" class="w-5 h-5"></i>
</button>
{% endblock %}

{% block mobile_back_button %}
<button onclick="history.back()" class="w-8 h-8 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center justify-center -ml-2">
    <i data-feather="arrow-left" class="w-5 h-5"></i>
</button>
{% endblock %}

{% block content %}
<div class="hidden md:flex items-center justify-between mb-8">
    <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Product Inventory</h1>
        <p class="text-slate-500 dark:text-slate-400">Manage your products and stock levels</p>
    </div>
    <button onclick="openModal()" class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary-600/20">
        <i data-feather="plus" class="w-4 h-4"></i>
        Add Product
    </button>
</div>

<div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-4 mb-6">
    <div class="flex flex-col md:flex-row gap-3">
        <div class="relative flex-1">
            <i data-feather="search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"></i>
            <form method="get" id="searchForm">
                <input type="text" name="q" id="productSearch" value="{{ search_query|default:'' }}" placeholder="Search products..." class="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800 border-none rounded-xl text-sm focus:ring-2 focus:ring-primary-500 placeholder-slate-400">
            </form>
        </div>
        <select id="stockFilter" onchange="filterProducts()" class="px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border-none rounded-xl text-sm focus:ring-2 focus:ring-primary-500 md:w-48">
            <option value="all">All Products</option>
            <option value="in-stock">In Stock</option>
            <option value="low-stock">Low Stock</option>
            <option value="out-of-stock">Out of Stock</option>
        </select>
    </div>
</div>

<div class="hidden md:block bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
    <table class="w-full">
        <thead class="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
            <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Product</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Category</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Price</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Stock</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Status</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Last Updated</th>
                <th class="px-6 py-4 text-right text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Actions</th>
            </tr>
        </thead>
        <tbody id="productTableBody" class="divide-y divide-slate-200 dark:divide-slate-800">
            {% for product in products %}
            <tr class="product-row hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors" data-stock-status="{% if product.stock_quantity == 0 %}out-of-stock{% elif product.is_low_stock %}low-stock{% else %}in-stock{% endif %}">
                <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 overflow-hidden">
                            {% if product.image %}
                                <img src="{{ product.image.url }}" alt="{{ product.name }}" class="w-full h-full object-cover">
                            {% else %}
                                <i data-feather="package" class="w-5 h-5 text-slate-400"></i>
                            {% endif %}
                        </div>
                        <div>
                            <p class="font-medium text-slate-900 dark:text-white">{{ product.name }}</p>
                            <p class="text-xs text-slate-500">{{ product.barcode|default:"No barcode" }}</p>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400">
                        {{ product.category.name|default:"Uncategorized" }}
                    </span>
                </td>
                <td class="px-6 py-4 font-semibold text-slate-900 dark:text-white">₦{{ product.price|intcomma }}</td>
                <td class="px-6 py-4 text-slate-600 dark:text-slate-400">{{ product.stock_quantity }}</td>
                <td class="px-6 py-4">
                    {% if product.stock_quantity == 0 %}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400">Out of Stock</span>
                    {% elif product.is_low_stock %}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400">Low Stock</span>
                    {% else %}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400">In Stock</span>
                    {% endif %}
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                    {{ product.updated_at|date:"M d, Y" }}
                </td>
                <td class="px-6 py-4 text-right">
                    <div class="flex items-center justify-end gap-2">
                        <a href="{% url 'product_update' product.pk %}" class="p-2 text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                            <i data-feather="edit-2" class="w-4 h-4"></i>
                        </a>
                        <a href="{% url 'product_delete' product.pk %}" class="p-2 text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors">
                            <i data-feather="trash-2" class="w-4 h-4"></i>
                        </a>
                    </div>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="7" class="px-6 py-12 text-center">
                    <div class="flex flex-col items-center text-slate-400">
                        <i data-feather="package" class="w-12 h-12 mb-3 opacity-20"></i>
                        <p class="font-medium">No products found</p>
                        <p class="text-sm">Get started by adding your first product</p>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="md:hidden space-y-3">
    {% for product in products %}
    <div class="mobile-card bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-4" data-stock-status="{% if product.stock_quantity == 0 %}out-of-stock{% elif product.is_low_stock %}low-stock{% else %}in-stock{% endif %}">
        <div class="flex items-start gap-3 mb-3">
            <div class="w-16 h-16 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 overflow-hidden">
                {% if product.image %}
                    <img src="{{ product.image.url }}" alt="{{ product.name }}" class="w-full h-full object-cover">
                {% else %}
                    <i data-feather="package" class="w-6 h-6 text-slate-400"></i>
                {% endif %}
            </div>
            <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-slate-900 dark:text-white truncate">{{ product.name }}</h3>
                <p class="text-xs text-slate-500 mb-1">
                    {{ product.category.name|default:"Uncategorized" }} • {{ product.updated_at|date:"M d" }}
                </p>
                <p class="text-lg font-bold text-primary-600 dark:text-primary-400">₦{{ product.price|intcomma }}</p>
            </div>
        </div>
        
        <div class="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-2">
                <span class="text-sm text-slate-600 dark:text-slate-400">Stock: <strong class="text-slate-900 dark:text-white">{{ product.stock_quantity }}</strong></span>
                {% if product.stock_quantity == 0 %}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400">Out</span>
                {% elif product.is_low_stock %}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400">Low</span>
                {% else %}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400">In Stock</span>
                {% endif %}
            </div>
            <a href="{% url 'product_update' product.pk %}" class="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-medium transition-colors">
                <i data-feather="edit-2" class="w-3 h-3"></i>
                Edit
            </a>
        </div>
    </div>
    {% empty %}
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-12 text-center">
        <div class="flex flex-col items-center text-slate-400">
            <i data-feather="package" class="w-12 h-12 mb-3 opacity-20"></i>
            <p class="font-medium">No products found</p>
            <button onclick="openModal()" class="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium">
                <i data-feather="plus" class="w-4 h-4"></i>
                Add Product
            </button>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}

{% block extra_js %}
<script>
    function filterProducts() {
        const filter = document.getElementById("stockFilter").value;
        const rows = document.querySelectorAll(".product-row, .mobile-card");
        
        rows.forEach((item) => {
            if (filter === "all" || item.dataset.stockStatus === filter) {
                item.style.display = "";
            } else {
                item.style.display = "none";
            }
        });
    }

    function openModal() {
        window.location.href = "{% url 'product_create' %}";
    }

    let searchTimeout;
    const productSearch = document.getElementById("productSearch");
    if (productSearch) {
        productSearch.addEventListener("input", function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                document.getElementById("searchForm").submit();
            }, 500);
        });
    }
</script>
{% endblock %}
'''

import os
filepath = 'templates/store/product_list.html'
with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print(f'Successfully updated {filepath}')
