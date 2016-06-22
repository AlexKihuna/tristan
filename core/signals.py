from django.db.models.signals import pre_save, post_save, pre_delete
from django.db.models import F, Q
from django.dispatch import receiver
from .models import (
    SalesOrder, SupplyOrder, SalesOrderPayment, SupplyOrderPayment,
    SalesOrderItem, SalesOrderItemDelivery
)


@receiver(pre_delete, sender=SalesOrder)
def pre_delete_sales_order(sender, instance, **kwargs):
    """Update the customers payment records."""
    customer = instance.customer  # remove the payment data on deletion
    customer.total_paid -= instance.total_paid
    customer.total_due -= instance.amount_due
    customer.save()


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
@receiver(pre_save, sender=SupplyOrder)
def pre_save_order(sender, instance, **kwargs):
    """Ensure correct payment status for all orders before saving"""
    # Add the payment status before saving
    instance.payment_status = instance.get_payment_status()
    instance.order_status = instance.get_order_status()


@receiver(pre_save, sender=SalesOrder, dispatch_uid="sales order pre save only")
def pre_save_sales_order(sender, instance, **kwargs):
    """Update customer payment records with the total paid/due"""
    if instance.id:
        old_instance = sender.objects.get(pk=instance.id)
        old_customer = old_instance.customer
        old_customer.total_paid -= old_instance.total_paid
        old_customer.total_due -= old_instance.amount_due
        old_customer.save()
    customer = instance.customer
    customer.total_paid += instance.total_paid
    customer.total_due += instance.amount_due
    import pdb;pdb.set_trace()
    customer.save()


@receiver(pre_save, sender=SupplyOrder)
def pre_save_sales_order(sender, instance, **kwargs):
    """Update supplier payment records with the total paid/due"""
    if instance.id:
        old_instance = sender.objects.get(pk=instance.id)
        old_supplier = old_instance.supplier
        old_supplier.total_paid -= old_instance.total_paid
        old_supplier.total_due -= old_instance.amount_due
        old_supplier.save()
    supplier = instance.supplier
    supplier.total_paid += instance.total_paid
    supplier.total_due += instance.amount_due
    supplier.save()


@receiver(pre_save, sender=SalesOrderPayment)
@receiver(pre_save, sender=SupplyOrderPayment)
def pre_save_order_payment(sender, instance, **kwargs):
    if not instance.payment_code:
        instance.payment_code = instance.get_payment_code()


@receiver(pre_save, sender=SalesOrderItem)
def pre_save_sales_order_item(sender, instance, **kwargs):
    """Ensure item is marked delivered before saving."""
    instance.is_delivered = (instance.quantity_delivered == instance.quantity_ordered)


@receiver(post_save, sender=SalesOrderItem)
def post_save_sales_item(sender, created, instance, **kwargs):
    # Update the order status
    instance.sales_order.save()


@receiver(post_save, sender=SalesOrderItemDelivery)
def post_save_sales_item_delivery(sender, created, instance, **kwargs):
    """Ensure item is marked delivered after saving a delivery."""
    instance.item.save()
