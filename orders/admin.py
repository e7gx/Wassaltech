from django.contrib import admin

from orders.models import Offer, Order

# Register your models here.
admin.site.site_header = "Order Management System"
admin.site.register(Order)
admin.site.register(Offer)