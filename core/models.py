from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db.models import Avg, Sum, Max, Min, Count, F, Q, ExpressionWrapper as E
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.timezone import now
from django.db import models
from uuid import uuid4

# All currency is in Kenya Shillings. TODO Support multi currency

CURRENCY = (
    ('KES', 'Kenyan Shilling'),
)

ITEM_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)

PAYMENT_STATUS = (
    ('pending payment', 'Pending Payment'),
    ('overdue', 'Overdue'),
    ('critical', 'Critical'),
    ('paid', 'Paid'),
)

ORDER_STATUS = (
    ('pending deliveries', 'Pending Deliveries'),
    ('complete', 'Complete'),
)


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY, default='KES')
    total_paid = models.DecimalField(
        max_digits=9, decimal_places=2, default=0, editable=False
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:customer', kwargs={'pk': self.pk})

    @property
    def total_orders(self):
        return self.salesorder_set.count()


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY, default='KES')
    total_paid = models.DecimalField(
        max_digits=9, decimal_places=2, default=0, editable=False
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:supplier', kwargs={'pk': self.pk})

    @property
    def total_orders(self):
        return self.supplyorder_set.count()


class Inventory(models.Model):
    item_name = models.CharField(max_length=255, unique=True)
    item_sku = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY, default='KES')
    unit_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    manage_stock = models.BooleanField(default=False, help_text='Manage stock at product level')
    quantity = models.IntegerField(default=0)
    min_threshold = models.IntegerField(default=0, help_text='Identifies level at which stock is considered low')
    item_status = models.CharField(
        max_length=20, choices=ITEM_STATUS, default=ITEM_STATUS[0][0]
    )

    class Meta:
        verbose_name = _('inventory')
        verbose_name_plural = _('inventory')

    def __str__(self):
        return self.item_name

    def get_absolute_url(self):
        return reverse('core:item', kwargs={'pk': self.pk})

    def has_stock(self):
        if self.manage_stock:
            return bool(self.quantity)
        else:
            return True


class ItemImage(models.Model):
    item = models.ForeignKey('Inventory')
    image = models.ImageField(upload_to='inventory', blank=True)

    def get_absolute_url(self):
        return reverse('core:item', kwargs={'pk': self.item.pk})


class SalesOrder(models.Model):
    order_code = models.IntegerField(editable=False, unique=True, null=True)
    customer = models.ForeignKey('Customer')
    items = models.ManyToManyField('Inventory', through='SalesOrderItem')
    order_date = models.DateTimeField()
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default=PAYMENT_STATUS[0][0],
        editable=False
    )
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS, default=ORDER_STATUS[0][0],
        editable=False
    )

    def __str__(self):
        return self.customer.name

    def get_absolute_url(self):
        return reverse('core:salesorder', kwargs={'pk': self.pk})

    @property
    def total_paid(self):
        queryset = self.salesorderpayment_set.aggregate(Sum('amount_paid'))
        return queryset['amount_paid__sum'] or 0

    @property
    def order_currency(self):
        return 'KES'

    @property
    def order_value(self):
        queryset = self.salesorderitem_set.aggregate(
            order_value=Sum(E(F('unit_price')*F('quantity_ordered'), output_field=models.DecimalField())),
        )
        return queryset['order_value'] or 0

    @property
    def amount_due(self):
        """Takes delivery into consideration and bills only delivered items"""
        queryset = self.salesorderitem_set.filter(is_delivered=False).aggregate(
            amount_due=Sum(E(F('unit_price')*F('quantity_ordered'), output_field=models.DecimalField()))
        )
        return queryset['amount_due'] or 0

    @property
    def is_paid(self):
        return self.total_paid >= self.amount_due

    @property
    def last_delivery_date(self):
        max_dates = [item.last_delivery_date for item in self.salesorderitem_set.all()
                     if item.last_delivery_date]
        if max_dates:
            return max(max_dates).date()
        return None

    @property
    def is_delivery_complete(self):
        return all([item.is_delivered for item in self.salesorderitem_set.all()])

    def get_payment_status(self):
        if self.is_paid:
            return 'paid'
        if not self.last_delivery_date:
            return 'pending payment'
        td = now() - self.last_delivery_date
        if td.days <= 30:
            return 'pending payment'
        if 30 < td.days <= 60:
            return 'overdue'
        if 60 < td.days:
            return 'critical'

    def get_order_status(self):
        if self.is_delivery_complete:
            return 'complete'
        return 'pending deliveries'


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey('SalesOrder')
    item = models.ForeignKey('Inventory')
    quantity_ordered = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY, default='KES')
    unit_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    is_delivered = models.BooleanField(default=False, editable=False)

    class Meta:
        unique_together = (("sales_order", "item"),)

    def __str__(self):
        return self.item.item_name

    def get_absolute_url(self):
        return reverse('core:salesorder', kwargs={'pk': self.sales_order.pk})

    @property
    def total_cost(self):
        return self.unit_price * self.quantity_ordered

    @property
    def quantity_delivered(self):
        queryset = self.salesorderitemdelivery_set.aggregate(Sum('quantity_delivered'))
        return queryset['quantity_delivered__sum'] or 0

    @property
    def last_delivery_date(self):
        queryset = self.salesorderitemdelivery_set.aggregate(Max('delivery_date'))
        return queryset['delivery_date__max'] or None


class SalesOrderItemDelivery(models.Model):
    item = models.ForeignKey('SalesOrderItem')
    quantity_delivered = models.IntegerField()
    delivery_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('sales order delivery')
        verbose_name_plural = _('sales order deliveries')

    def __str__(self):
        return '%s (%s)' % (self.item.item.item_name,
                            self.quantity_delivered)

    def get_absolute_url(self):
        return reverse('core:salesorder', kwargs={'pk': self.item.sales_order.pk})


class SalesOrderPayment(models.Model):
    sales_order = models.ForeignKey('SalesOrder')
    payment_code = models.CharField(max_length=30, unique=True, editable=False)
    currency = models.CharField(max_length=3, choices=CURRENCY, default='KES')
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    date_paid = models.DateTimeField()

    def __str__(self):
        return '%s - %s %s' % (self.sales_order.order_code, self.currency, self.amount_paid)

    def get_absolute_url(self):
        return reverse('core:salesorder', kwargs={'pk': self.sales_order.pk})

    def get_payment_code(self):
        return str(self.sales_order.order_code) + str(uuid4()).split('-')[0]


class SupplyOrder(models.Model):
    order_code = models.IntegerField(editable=False, unique=True, null=True)
    supplier = models.ForeignKey('Supplier')
    items = models.ManyToManyField('Inventory', through='SupplyOrderItem')
    order_date = models.DateTimeField()
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default=PAYMENT_STATUS[0][0],
        editable=False
    )
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS, default=ORDER_STATUS[0][0],
        editable=False
    )

    def __str__(self):
        return self.supplier.name

    def get_absolute_url(self):
        return reverse('core:supplyorder', kwargs={'pk': self.pk})

    @property
    def total_paid(self):
        queryset = self.supplyorderpayment_set.aggregate(Sum('amount_paid'))
        return queryset['amount_paid__sum'] or 0

    @property
    def order_value(self):
        queryset = self.supplyorderitem_set.aggregate(
            order_value=Sum(F('unit_price')*F('quantity_ordered'))
        )
        return queryset['order_value'] or 0

    @property
    def amount_due(self):
        """Takes delivery into consideration and bills only delivered items"""
        queryset = self.supplyorderitem_set.filter(delivery_date__isnull=False).aggregate(
            amount_due=Sum(F('unit_price')*F('quantity_ordered'))
        )
        return queryset['amount_due'] or 0

    @property
    def is_paid(self):
        return self.total_paid >= self.amount_due

    @property
    def last_delivery_date(self):
        max_dates = [item.last_delivery_date for item in self.supplyorderitem_set.all()
                     if item.last_delivery_date]
        if max_dates:
            return max(max_dates).date()
        return None

    @property
    def is_delivery_complete(self):
        return all([item.is_delivered for item in self.supplyorderitem_set.all()])

    def get_payment_status(self):
        if self.is_paid:
            return 'paid'
        if not self.last_delivery_date:
            return 'pending_payment'
        td = now() - self.last_delivery_date
        if td.days <= 30:
            return 'pending_payment'
        if 30 < td.days <= 60:
            return 'overdue'
        if 60 < td.days:
            return 'critical'

    def get_order_status(self):
        if self.delivery_complete:
            return 'complete'
        return 'pending'


class SupplyOrderItem(models.Model):
    supply_order = models.ForeignKey('SupplyOrder')
    item = models.ForeignKey('Inventory')
    quantity_ordered = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY, default='KES')
    unit_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    delivery_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.item.item_name

    @property
    def total_cost(self):
        return self.unit_price * self.quantity_ordered

    @property
    def quantity_delivered(self):
        queryset = self.supplyorderitemdelivery_set.aggregate(Sum('quantity_delivered'))
        return queryset['quantity_delivered__sum'] or 0

    @property
    def is_delivered(self):
        return self.quantity_delivered == self.quantity_ordered

    @property
    def last_delivery_date(self):
        queryset = self.supplyorderitemdelivery_set.aggregate(Max('delivery_date'))
        return queryset['delivery_date__max'] or None


class SupplyOrderItemDelivery(models.Model):
    item = models.ForeignKey('SupplyOrderItem')
    quantity_delivered = models.IntegerField()
    delivery_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('sales order delivery')
        verbose_name_plural = _('sales order deliveries')

    def __str__(self):
        return '%s (%s)' % (self.item.item.item_name,
                            self.quantity_delivered)


class SupplyOrderPayment(models.Model):
    supply_order = models.ForeignKey('SupplyOrder')
    currency = models.CharField(max_length=3, choices=CURRENCY, default='KES')
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    date_paid = models.DateTimeField()

    def __str__(self):
        return '%s - %s %s' % (self.supply_order.order_code, self.currency, self.amount_paid)
