from django import forms
from .models import (
    Customer, Supplier, SalesOrder, SupplyOrder, SalesOrderPayment,
    SupplyOrderPayment, SalesOrderItem, SupplyOrderItem, Inventory,
    ItemImage
)


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'order_date']
        widgets = {
            'order_date': forms.DateInput(attrs={'class':'datepicker'}),
        }


class SalesOrderPaymentForm(forms.ModelForm):
    class Meta:
        model = SalesOrderPayment
        fields = ['currency', 'amount_paid', 'date_paid']
        widgets = {
            'date_paid': forms.DateInput(attrs={'class':'datepicker'}),
        }