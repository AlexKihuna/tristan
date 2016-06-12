from django.db.models.signals import pre_save, post_save
from django.db.models import F, Q
from django.dispatch import receiver
from .models import (
    SalesOrder, SupplyOrder, SalesOrderPayment, SupplyOrderPayment,
    SalesOrderItem, SalesOrderItemDelivery
)


@receiver(post_save, sender=SalesOrder)
def post_save_sales_order(sender, created, instance, **kwargs):
    """Add the order code for new orders."""
    if created:  # A new order has been created
        instance.order_code = instance.id + 1000
        instance.save()


@receiver(post_save, sender=SupplyOrder)
def post_save_supply_order(sender, created, instance, **kwargs):
    """Add the order code for new orders"""
    if created:  # A new order has been created
        instance.order_code = instance.id + 3000
        instance.save()


@receiver(pre_save, sender=SalesOrder)
def pre_save_sales_order(sender, instance, **kwargs):
    """Ensure correct payment status for all orders before saving"""
    # Add the payment status before saving
    instance.payment_status = instance.get_payment_status()
    instance.order_status = instance.get_order_status()


@receiver(pre_save, sender=SupplyOrder)
def pre_save_sales_order(sender, instance, **kwargs):
    """Ensure correct payment status for all orders before saving"""
    # Add the payment status before saving
    instance.payment_status = instance.get_payment_status()
    instance.order_status = instance.get_order_status()


@receiver(pre_save, sender=SalesOrderPayment)
def pre_save_sales_order_payment(sender, instance, **kwargs):
    """Ensure customer has updated payment records."""
    if instance.id:
        old_instance = sender.objects.get(pk=instance.id)
        old_customer = old_instance.sales_order.customer
        old_customer.total_paid -= old_instance.total_paid
        old_customer.save()
    customer = instance.sales_order.customer
    customer.total_paid += instance.amount_paid
    customer.save()


@receiver(pre_save, sender=SupplyOrderPayment)
def pre_save_supply_order_payment(sender, instance, **kwargs):
    """Ensure supplier has updated payment records."""
    if instance.id:
        old_instance = sender.objects.get(pk=instance.id)
        old_supplier = old_instance.supply_order.supplier
        old_supplier.total_paid -= old_instance.total_paid
        old_supplier.save()
    supplier = instance.supply_order.supplier
    supplier.total_paid += instance.amount_paid
    supplier.save()


@receiver(pre_save, sender=SalesOrderItem)
def pre_save_sales_order_item(sender, instance, **kwargs):
    """Ensure item is marked delivered before saving."""
    if instance.quantity_delivered == instance.quantity_ordered:
        instance.is_delivered = True


@receiver(post_save, sender=SalesOrderItemDelivery)
def post_save_sales_item_delivery(sender, created, instance, **kwargs):
    """Ensure item is marked delivered after saving a delivery."""
    item = instance.item
    if item.quantity_delivered == item.quantity_ordered:
        item.is_delivered = True
        item.save()
