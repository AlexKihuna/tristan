from django.conf.urls import include, url
from . import views

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^customers/(?P<page>[0-9]+)?$', views.CustomerListView.as_view(), name='customer_list'),
    url(r'^customers/id/(?P<pk>[0-9]+)?$', views.CustomerDetailView.as_view(), name='customer'),
    url(r'^customers/add/$', views.CustomerCreateView.as_view(), name='customer_add'),
    url(r'^customers/update/id/(?P<pk>[0-9]+)$', views.CustomerUpdateView.as_view(), name='customer_edit'),
    url(r'^suppliers/(?P<page>[0-9]+)?$', views.SupplierListView.as_view(), name='supplier_list'),
    url(r'^suppliers/id/(?P<pk>[0-9]+)?$', views.SupplierDetailView.as_view(), name='supplier'),
    url(r'^suppliers/add/$', views.SupplierCreateView.as_view(), name='supplier_add'),
    url(r'^suppliers/update/id/(?P<pk>[0-9]+)$', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    url(r'^salesorders/(?P<page>[0-9]+)?$', views.SalesOrderListView.as_view(), name='salesorder_list'),
    url(r'^salesorders/id/(?P<pk>[0-9]+)?$', views.SalesOrderDetailView.as_view(), name='salesorder'),
    url(r'^salesorders/add/$', views.SalesOrderCreateView.as_view(), name='salesorder_add'),
    url(r'^salesorders/update/id/(?P<pk>[0-9]+)$', views.SalesOrderUpdateView.as_view(), name='salesorder_edit'),
    url(r'^salesorders/id/item/add/(?P<pk>[0-9]+)$', views.SalesOrderItemCreateView.as_view(), name='salesorderitem_add'),
    url(r'^salesorders/id/payment/add/(?P<pk>[0-9]+)$', views.SalesOrderPaymentCreateView.as_view(), name='salesorderpayment_add'),
    url(r'^supplyorders/(?P<page>[0-9]+)?$', views.SupplierListView.as_view(), name='supplyorder_list'),
    url(r'^supplyorders/id/(?P<pk>[0-9]+)?$', views.SupplierDetailView.as_view(), name='supplyorder'),
    url(r'^inventory/(?P<page>[0-9]+)?$', views.InventoryListView.as_view(), name='inventory'),
    url(r'^inventory/id/(?P<pk>[0-9]+)?$', views.InventoryDetailView.as_view(), name='item'),
    url(r'^inventory/add/$', views.InventoryCreateView.as_view(), name='inventory_add'),
    url(r'^inventory/update/id/(?P<pk>[0-9]+)$', views.InventoryUpdateView.as_view(), name='inventory_edit'),
    url(r'^inventory/id/image/add/(?P<pk>[0-9]+)$', views.ImageCreateView.as_view(), name='item_image_add'),
]
