from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from django.shortcuts import render, render_to_response
from django.core.urlresolvers import reverse_lazy, reverse
from django.template import RequestContext
from django.db.models import Avg, Sum, Max, Min, Count, F, Q
from .models import (
    Customer, Supplier, SalesOrder, SupplyOrder, SalesOrderPayment,
    SupplyOrderPayment, SalesOrderItem, SupplyOrderItem, Inventory,
    ItemImage, SalesOrderItemDelivery
)
from .forms import SalesOrderPaymentForm, SalesOrderForm, ItemDeliveryForm
from .mixin import AjaxableResponseMixin


def index(request):
    total_customers = Customer.objects.count()
    total_suppliers = Supplier.objects.count()
    total_sales_orders = SalesOrder.objects.count()
    total_supply_orders = SupplyOrder.objects.count()
    revenue = SalesOrderPayment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    credit = 0
    expenditure = SupplyOrderPayment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    debit = 0
    del_orders = SalesOrder.objects.filter(order_status='pending_deliveries').count()
    unpaid_sales = SalesOrder.objects.exclude(payment_status='paid')
    total_unpaid_sales = unpaid_sales.count()
    unpaying_customers = unpaid_sales.distinct('customer').count()
    unpaid_purchase = SupplyOrder.objects.exclude(payment_status='paid')
    total_unpaid_purchases = unpaid_purchase.count()
    unpaid_suppliers = unpaid_purchase.distinct('supplier').count()
    low_items = Inventory.objects.filter(quantity__lte=F('min_threshold')).count()
    data = {
        'total_sales_orders': total_sales_orders, 'revenue': revenue,
        'expenditure': expenditure, 'total_supply_orders': total_supply_orders,
        'credit': credit, 'debit': debit, 'total_customers': total_customers,
        'total_suppliers': total_suppliers, 'del_orders': del_orders,
        'low_items': low_items, 'total_unpaid_sales': total_unpaid_sales,
        'unpaying_customers': unpaying_customers,
        'total_unpaid_purchases': total_unpaid_purchases,
        'unpaid_suppliers': unpaid_suppliers,
    }
    return render_to_response('core/index.html', data)


class CustomerListView(ListView):
    model = Customer
    template_name = 'core/customer_list.html'
    context_object_name = 'customers'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        if search:
            queryset = self.model.objects.filter(
                Q(username__icontains=search) | Q(surname__icontains=search) |
                Q(other_names__icontains=search) | Q(email__icontains=search) |
                Q(contact_phone__icontains=search)
            )
        else:
            queryset = self.model.objects.all()
        return queryset


class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'core/customer.html'
    context_object_name = 'customer'


class CustomerCreateView(AjaxableResponseMixin, CreateView):
    model = Customer
    fields = ['name', 'email', 'contact_phone']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(CustomerCreateView, self).get_context_data(**kwargs)
        context['page_title'] = "Add Customer"
        return context


class CustomerUpdateView(AjaxableResponseMixin, UpdateView):
    model = Customer
    fields = ['name', 'email', 'contact_phone']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(CustomerUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = "Edit %s" % context['object'].name
        return context


class SupplierListView(ListView):
    model = Supplier
    template_name = 'core/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        if search:
            queryset = self.model.objects.filter(
                Q(username__icontains=search) | Q(surname__icontains=search) |
                Q(other_names__icontains=search) | Q(email__icontains=search) |
                Q(contact_phone__icontains=search)
            )
        else:
            queryset = self.model.objects.all()
        return queryset


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'core/supplier.html'
    context_object_name = 'supplier'


class SupplierCreateView(AjaxableResponseMixin, CreateView):
    model = Supplier
    fields = ['name', 'email', 'contact_phone']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierCreateView, self).get_context_data(**kwargs)
        context['page_title'] = "Add Supplier"
        return context


class SupplierUpdateView(AjaxableResponseMixin, UpdateView):
    model = Supplier
    fields = ['name', 'email', 'contact_phone']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SupplierUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = "Edit %s" % context['object'].name
        return context


class SalesOrderListView(ListView):
    model = SalesOrder
    template_name = 'core/salesorder_list.html'
    context_object_name = 'salesorder'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        if search:
            queryset = self.model.objects.filter(
                Q(username__icontains=search) | Q(surname__icontains=search) |
                Q(other_names__icontains=search) | Q(email__icontains=search) |
                Q(contact_phone__icontains=search)
            )
        else:
            queryset = self.model.objects.all()
        return queryset


class SalesOrderDetailView(DetailView):
    model = SalesOrder
    template_name = 'core/salesorder.html'
    context_object_name = 'salesorder'


class SalesOrderCreateView(AjaxableResponseMixin, CreateView):
    form_class = SalesOrderForm
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SalesOrderCreateView, self).get_context_data(**kwargs)
        context['page_title'] = "Add Sales Order"
        return context


class SalesOrderUpdateView(AjaxableResponseMixin, UpdateView):
    form_class = SalesOrderForm
    model = SalesOrder
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SalesOrderUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = "Edit Sales Order %s" % context['object'].order_code
        return context


class SalesOrderDeleteView(AjaxableResponseMixin, DeleteView):
    model = SalesOrder
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('core:salesorder_list')

    def get_context_data(self, **kwargs):
        context = super(SalesOrderDeleteView, self).get_context_data(**kwargs)
        context['page_title'] = "Delete Sales Order %s" % context['object'].order_code
        return context


class SalesOrderItemCreateView(AjaxableResponseMixin, CreateView):
    model = SalesOrderItem
    fields = ['item', 'quantity_ordered', 'currency', 'unit_price']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SalesOrderItemCreateView, self).get_context_data(**kwargs)
        sales_order = SalesOrder.objects.get(pk=self.kwargs['pk'])
        context['page_title'] = "Sales Order %s: Add Item" % sales_order.order_code
        return context

    def form_valid(self, form):
        sales_order = SalesOrder.objects.get(pk=self.kwargs['pk'])
        form.instance.sales_order = sales_order
        return super(SalesOrderItemCreateView, self).form_valid(form)


class SalesOrderItemUpdateView(AjaxableResponseMixin, UpdateView):
    model = SalesOrderItem
    fields = ['item', 'quantity_ordered', 'currency', 'unit_price']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SalesOrderItemUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = "Sales Order %s: Edit Item" % context['object'].sales_order.order_code
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.sales_order = context['object'].sales_order
        return super(SalesOrderItemUpdateView, self).form_valid(form)


class SalesOrderItemDeleteView(AjaxableResponseMixin, DeleteView):
    model = SalesOrderItem
    template_name = 'core/confirm_delete.html'
    # success_url = reverse_lazy('core:salesorder')

    def get_success_url(self):
        context = self.get_context_data()
        return reverse_lazy('core:salesorder', kwargs={'pk': context['object'].pk})

    def get_context_data(self, **kwargs):
        context = super(SalesOrderItemDeleteView, self).get_context_data(**kwargs)
        context['page_title'] = "Delete Sales Order Item %s" % context['object'].item.item_name
        return context


class SalesOrderDeliveryCreateView(AjaxableResponseMixin, CreateView):
    form_class = ItemDeliveryForm
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SalesOrderDeliveryCreateView, self).get_context_data(**kwargs)
        item = SalesOrderItem.objects.get(pk=self.kwargs['pk'])
        context['page_title'] = "Sales Order %s: Add %s Delivery" % (
            item.sales_order.order_code, item.item.item_name
        )
        return context

    def form_valid(self, form):
        item = SalesOrderItem.objects.get(pk=self.kwargs['pk'])
        form.instance.item = item
        return super(SalesOrderDeliveryCreateView, self).form_valid(form)


class SalesOrderPaymentCreateView(AjaxableResponseMixin, CreateView):
    form_class = SalesOrderPaymentForm
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SalesOrderPaymentCreateView, self).get_context_data(**kwargs)
        sales_order = SalesOrder.objects.get(pk=self.kwargs['pk'])
        context['page_title'] = "Sales Order %s: Add Payment" % sales_order.order_code
        return context

    def form_valid(self, form):
        sales_order = SalesOrder.objects.get(pk=self.kwargs['pk'])
        form.instance.sales_order = sales_order
        return super(SalesOrderPaymentCreateView, self).form_valid(form)


class SalesOrderPaymentUpdateView(AjaxableResponseMixin, UpdateView):
    model = SalesOrderPayment
    form_class = SalesOrderPaymentForm
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(SalesOrderPaymentUpdateView, self).get_context_data(**kwargs)
        sales_order = SalesOrder.objects.get(pk=self.kwargs['pk'])
        context['page_title'] = "Sales Order %s: Edit Item" % sales_order.order_code
        return context

    def form_valid(self, form):
        sales_order = SalesOrder.objects.get(pk=self.kwargs['pk'])
        form.instance.sales_order = sales_order
        return super(SalesOrderPaymentUpdateView, self).form_valid(form)


class SalesOrderPaymentDeleteView(AjaxableResponseMixin, DeleteView):
    model = SalesOrderPayment
    template_name = 'core/confirm_delete.html'
    # success_url = reverse_lazy('core:salesorder')

    def get_success_url(self):
        context = self.get_context_data()
        return reverse_lazy('core:salesorder', kwargs={'pk': context['object'].pk})

    def get_context_data(self, **kwargs):
        context = super(SalesOrderPaymentDeleteView, self).get_context_data(**kwargs)
        context['page_title'] = "Delete Sales Order Item %s" % context['object'].item.item_name
        return context


class InventoryListView(ListView):
    model = Inventory
    template_name = 'core/inventory_list.html'
    context_object_name = 'inventory'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        if search:
            queryset = self.model.objects.filter(
                Q(item_name__icontains=search) | Q(item_sku__icontains=search)
            )
        else:
            queryset = self.model.objects.all()
        return queryset


class InventoryDetailView(DetailView):
    model = Inventory
    template_name = 'core/item.html'
    context_object_name = 'item'


class InventoryCreateView(AjaxableResponseMixin, CreateView):
    model = Inventory
    fields = ['item_name', 'item_sku', 'description', 'currency', 'unit_price', 'quantity', 'min_threshold']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(InventoryCreateView, self).get_context_data(**kwargs)
        context['page_title'] = "Add Inventory Item"
        return context


class InventoryUpdateView(AjaxableResponseMixin, UpdateView):
    model = Inventory
    fields = ['item_name', 'item_sku', 'description', 'currency', 'unit_price', 'quantity', 'min_threshold']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(InventoryUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = "Edit %s" % context['object'].item_name
        return context


class ImageCreateView(AjaxableResponseMixin, CreateView):
    model = ItemImage
    fields = ['image']
    template_name = 'core/form.html'

    def get_context_data(self, **kwargs):
        context = super(ImageCreateView, self).get_context_data(**kwargs)
        item = Inventory.objects.get(pk=self.kwargs['pk'])
        context['page_title'] = "Add Image: %s" % item.item_name
        return context

    def form_valid(self, form):
        item = Inventory.objects.get(pk=self.kwargs['pk'])
        form.instance.item = item
        return super(ImageCreateView, self).form_valid(form)
