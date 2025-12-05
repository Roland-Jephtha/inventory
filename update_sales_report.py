content = r'''{% extends 'layouts/app.html' %}
{% load humanize %}

{% block title %}Sales Report - POS-Lite{% endblock %}

{% block mobile_back_button %}
<button onclick="history.back()" class="w-8 h-8 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center justify-center -ml-2">
    <i data-feather="arrow-left" class="w-5 h-5"></i>
</button>
{% endblock %}

{% block appbar_title %}Sales Report{% endblock%}

{% block content %}
<!-- Header -->
<div class="mb-8 print-content">
  <h1 class="text-2xl font-bold text-slate-900 dark:text-white">
    Sales Reports
  </h1>
  <p class="text-slate-500 dark:text-slate-400">
    Track your sales performance and trends
  </p>
</div>

<!-- Filters -->
<div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-4 mb-6 no-print">
  <form method="get" class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div>
      <label class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 block">Start Date</label>
      <input type="date" name="start_date" value="{{ start_date|default:'' }}" class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border-none rounded-xl text-sm focus:ring-2 focus:ring-primary-500"/>
    </div>
    <div>
      <label class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 block">End Date</label>
      <input type="date" name="end_date" value="{{ end_date|default:'' }}" class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border-none rounded-xl text-sm focus:ring-2 focus:ring-primary-500"/>
    </div>
    <div class="flex items-end gap-2">
      <button type="submit" class="flex-1 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium transition-colors shadow-lg shadow-primary-600/20 flex items-center justify-center gap-2">
        <i data-feather="filter" class="w-4 h-4"></i>
        Filter
      </button>
      <button type="submit" name="export" value="csv" class="px-4 py-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-medium transition-colors flex items-center justify-center gap-2" title="Export CSV">
        <i data-feather="download" class="w-4 h-4"></i>
      </button>
      <button type="button" onclick="window.print()" class="px-4 py-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-medium transition-colors flex items-center justify-center gap-2" title="Print / Save PDF">
        <i data-feather="printer" class="w-4 h-4"></i>
      </button>
    </div>
  </form>
</div>

<style>
@media print {
    body * {
        visibility: hidden;
    }
    .print-content, .print-content * {
        visibility: visible;
    }
    .print-content {
        position: relative;
        left: 0;
        top: 0;
        width: 100%;
    }
    /* Hide non-printable elements */
    nav, header, .no-print {
        display: none !important;
    }
    /* Ensure table fits */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
    }
}
</style>

<!-- Stats Grid -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 print-content">
  <div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
    <div class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-4">
      <i data-feather="dollar-sign" class="w-5 h-5"></i>
    </div>
    <p class="text-sm text-slate-500 dark:text-slate-400">Total Revenue</p>
    <h3 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white mt-1">
      ₦{{ total_sales|default:0|floatformat:2|intcomma }}
    </h3>
  </div>

  <div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
    <div class="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-4">
      <i data-feather="shopping-bag" class="w-5 h-5"></i>
    </div>
    <p class="text-sm text-slate-500 dark:text-slate-400">Total Sales</p>
    <h3 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white mt-1">
      {{ sales_count|default:0 }}
    </h3>
  </div>

  <div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
    <div class="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-4">
      <i data-feather="trending-up" class="w-5 h-5"></i>
    </div>
    <p class="text-sm text-slate-500 dark:text-slate-400">Average Sale</p>
    <h3 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white mt-1">
      ₦{{ average_sale|default:0|floatformat:2|intcomma }}
    </h3>
  </div>

  <div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
    <div class="w-10 h-10 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 flex items-center justify-center mb-4">
      <i data-feather="package" class="w-5 h-5"></i>
    </div>
    <p class="text-sm text-slate-500 dark:text-slate-400">Items Sold</p>
    <h3 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white mt-1">
      {{ items_sold|default:0 }}
    </h3>
  </div>
</div>

<!-- Sales Table -->
<div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden print-content">
  <div class="p-6 border-b border-slate-200 dark:border-slate-800">
    <h3 class="text-lg font-bold text-slate-900 dark:text-white">
      Recent Sales
    </h3>
  </div>

  <!-- Desktop Table -->
  <div class="hidden md:block overflow-x-auto">
    <table class="w-full">
      <thead class="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <tr>
          <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Date</th>
          <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Customer</th>
          <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Payment</th>
          <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Items</th>
          <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Total</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-200 dark:divide-slate-800">
        {% for sale in sales %}
        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
          <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
            {{ sale.created_at|date:"M j, Y - g:i A" }}
          </td>
          <td class="px-6 py-4 text-sm font-medium text-slate-900 dark:text-white">
            {{ sale.customer.name|default:"Walk-in" }}
          </td>
          <td class="px-6 py-4">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400">
              {{ sale.get_payment_method_display }}
            </span>
          </td>
          <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
            {{ sale.saleitem_set.count }}
          </td>
          <td class="px-6 py-4 text-sm font-bold text-emerald-600 dark:text-emerald-400">
            ₦{{ sale.total_amount|intcomma }}
          </td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="5" class="px-6 py-12 text-center">
            <div class="flex flex-col items-center text-slate-400">
              <i data-feather="bar-chart-2" class="w-12 h-12 mb-3 opacity-20"></i>
              <p class="font-medium">No sales data</p>
              <p class="text-sm">Sales will appear here once transactions are completed</p>
            </div>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <!-- Mobile Cards -->
  <div class="md:hidden p-4 space-y-3">
    {% for sale in sales %}
    <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
      <div class="flex items-start justify-between mb-3">
        <div>
          <p class="font-medium text-slate-900 dark:text-white">
            {{ sale.customer.name|default:"Walk-in" }}
          </p>
          <p class="text-xs text-slate-500">
            {{ sale.created_at|date:"M j, Y - g:i A" }}
          </p>
        </div>
        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400">
          {{ sale.get_payment_method_display }}
        </span>
      </div>
      <div class="flex items-center justify-between pt-3 border-t border-slate-200 dark:border-slate-700">
        <span class="text-sm text-slate-600 dark:text-slate-400">{{ sale.saleitem_set.count }} items</span>
        <span class="text-lg font-bold text-emerald-600 dark:text-emerald-400">₦{{ sale.total_amount|intcomma }}</span>
      </div>
    </div>
    {% empty %}
    <div class="py-12 text-center">
      <div class="flex flex-col items-center text-slate-400">
        <i data-feather="bar-chart-2" class="w-12 h-12 mb-3 opacity-20"></i>
        <p class="font-medium">No sales data</p>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
'''

import os
filepath = 'templates/store/sales_report.html'
with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print(f'Successfully updated {filepath}')
