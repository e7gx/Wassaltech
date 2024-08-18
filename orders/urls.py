from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('freelancer/', views.freelancer_orders, name='freelancer_orders'),
    path('offer/create/<int:order_id>/', views.create_offer, name='create_offer'),
    path('offers/<int:order_id>/', views.order_offers, name='order_offers'),
    path('offer/accept/<int:offer_id>/', views.accept_offer, name='accept_offer'),
    path('payment/<int:offer_id>/', views.fake_payment, name='fake_payment'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('end-order/<int:order_id>/', views.end_order, name='end_order'),
    path('history/', views.order_history, name='order_history'),
    path('customer/orders/', views.customer_orders, name='customer_orders'),
    path('freelancer/offers/', views.freelancer_offers, name='freelancer_offers'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]
