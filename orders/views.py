from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from notifications.views import NotificationService as sendemail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import user_type_required
from .forms import OrderForm, OfferForm
from reviews.forms import ReviewForm
from .models import Order, OrderImage, OrderVideo, Offer
from accounts.models import Account
from datetime import datetime, timedelta


########################################################################################################################
# ORDER CRUD
########################################################################################################################
########################################################################################################################
# ORDER CREATE
########################################################################################################################
# CUSTOMER CREATE
@login_required
def create_order(request):
    if request.method == 'POST':

        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user.account
            order.save()

            files = request.FILES.getlist('files')
            for file in files:
                OrderImage.objects.create(order=order, image=file)

            video = form.cleaned_data.get('video')
            if video:
                OrderVideo.objects.create(order=order, video=video)

            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})


########################################################################################################################
# ORDER READ
########################################################################################################################
# CUSTOMER READ
@login_required
def customer_orders(request):
    orders = Order.objects.filter(customer=request.user.account)
    return render(request, 'orders/customer_orders.html', {'orders': orders})


# CUSTOMER READ
# ! edit  this function
@login_required
def order_history(request):
    user = request.user
    if hasattr(user, 'account'):
        orders = Order.objects.filter(customer=user.account).exclude(status='Open')
    elif hasattr(user, 'freelancer'):
        orders = Order.objects.filter(assigned_to=user.freelancer).exclude(status='Open')
    else:
        orders = []
    return render(request, 'orders/order_history.html', {'orders': orders})


# FREELANCER READ
@login_required
def freelancer_orders(request):
    freelancer = request.user.freelancer
    orders = Order.objects.filter(status='Open')
    orders = orders.exclude(offer__freelancer=freelancer)
    return render(request, 'orders/freelancer_orders.html', {'orders': orders})


# MUTUAL READ
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    offer = Offer.objects.filter(order=order, stage='Accepted').first()
    order_images = OrderImage.objects.filter(order=order)  # Get all images for the order
    review_form = None

    if request.user == order.customer and not order.customer_completed:
        review_form = ReviewForm()

    context = {
        'order': order,
        'offer': offer,
        'review_form': review_form,
        'order_images': order_images,
    }
    return render(request, 'orders/order_detail.html', context)


########################################################################################################################
# ORDER UPDATE
########################################################################################################################
# MUTUAL UPDATE
@login_required
def end_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    offer = Offer.objects.filter(order=order_id, stage='Accepted').first()
    if hasattr(request.user, 'freelancer'):
        print(f"request.user.freelancer: {request.user.freelancer}")
    if hasattr(request.user, 'freelancer') and request.user.freelancer == order.assigned_to:
        order.freelancer_completed = True
        order.save()
        messages.success(request,
                         'You have successfully marked the order as closed. The customer can now finalize the order.')
    elif hasattr(request.user, 'account') and request.user.account == order.customer:
        if order.freelancer_completed:
            order.customer_completed = True
            order.status = 'Closed'
            order.save()
            offer.stage = 'Completed'
            # Logic for complete on time
            complete_on_time = (offer.proposed_service_date - datetime.now().date()).days >= 0
            if complete_on_time:
                offer.complete_on_time = True
            offer.save()
            messages.success(request, 'You have successfully closed the order.')
        else:
            messages.error(request, 'The freelancer must close the order before you can finalize it.')

    if request.user.account.user_type == 'Customer':
        return redirect('orders:customer_orders')
    else:
        return redirect('orders:freelancer_orders')


########################################################################################################################
# ORDER DELETE
########################################################################################################################
# CUSTOMER DELETE
# An order can be discarded if and only if its status is "Open".
@login_required
def customer_discard_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'Open':
        order.status = 'Discarded'
        order.save()
        messages.success(request, 'The order has been successfully discarded.')
    else:
        messages.error(request, 'This order cannot be discarded as it has already been linked with a freelancer.')

    return redirect('orders:customer_orders')


########################################################################################################################
# OFFER CRUD
########################################################################################################################
########################################################################################################################
# OFFER CREATE
########################################################################################################################
# FREELANCER CREATE
@login_required
def create_offer(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_images = OrderImage.objects.filter(order=order)  # Get all images for the order

    freelancer = request.user.freelancer

    if Offer.objects.filter(order=order, freelancer=freelancer).exists():
        messages.error(request, "You have already made an offer for this order.")
        return redirect('orders:freelancer_orders')

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.order = order
            offer.freelancer = freelancer
            offer.save()
            sendemail.notify_new_offer(freelancer , order , offer.price )
            messages.success(request, "Your offer has been submitted successfully.")
            return redirect('orders:freelancer_orders')
    else:
        form = OfferForm()
    return render(request, 'orders/create_offer.html', {'form': form, 'order': order,"order_images":order_images})


########################################################################################################################
# OFFER READ
########################################################################################################################
# CUSTOMER READ
@login_required
def order_offers(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.account)
    order_images = OrderImage.objects.filter(order=order)  # Get all images for the order
    offers = Offer.objects.filter(order=order).select_related('freelancer', 'freelancer__user')

    context = {
        'order': order,
        'offers': offers,
        'order_images': order_images,
    }

    return render(request, 'orders/order_offers.html', context)


# FREELANCER READ
@login_required
def freelancer_offers(request):
    offers = Offer.objects.filter(freelancer=request.user.freelancer)
    return render(request, 'orders/freelancer_offers.html', {'offers': offers})


########################################################################################################################
# OFFER UPDATE
########################################################################################################################
# CUSTOMER UPDATE
@login_required
def accept_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if request.user.account != order.customer:
        return HttpResponseForbidden("You don't have permission to accept this offer.")
    offer.stage = 'Accepted'
    offer.save()
    order.status = 'In Progress'
    order.assigned_to = offer.freelancer
    order.save()
    unaccepted_offers = Offer.objects.filter(order=order).exclude(id=offer_id)
    for unaccepted_offer in unaccepted_offers:
        unaccepted_offer.stage = 'Declined'
        unaccepted_offer.save()

    sendemail.notify_order_accepted(offer , order )

    return redirect('orders:order_detail', order_id=order.id)


# CUSTOMER UPDATE
# An offer can be cancelled if and only if it is in the "Accepted" stage.
@login_required
def customer_cancel_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if request.user.account != order.customer:
        return HttpResponseForbidden("You don't have permission to cancel this offer.")
    full_refund = timedelta(hours=24)
    half_refund = timedelta(hours=12)
    time_until_visit = offer.appointment - datetime.now()
    try:
        if time_until_visit >= full_refund:
            offer.refund = offer.price
            offer.price = 0
        elif time_until_visit >= half_refund:
            offer.refund = offer.price / 2
            offer.price = offer.price / 2

        offer.stage = 'Cancelled'
        offer.save()

        order.status = 'Open'
        order.assigned_to = None
        order.save()
    except Exception as e:
        print(e)

    return redirect('orders:order_detail', order_id=order.id)


# FREELANCER UPDATE
# An offer can be cancelled if and only if it is in the "Accepted" stage.
@login_required
def freelancer_cancel_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if request.user.account != order.assigned_to:
        return HttpResponseForbidden("You don't have permission to cancel this offer.")
    try:
        offer.stage = 'Cancelled'
        offer.refund = offer.price
        offer.price = 0
        offer.save()
        offer.freelancer.update_internal_rating()

        order.status = 'Open'
        order.assigned_to = None
        order.save()
    except Exception as e:
        print(e)

    return redirect('orders:freelancer_offers', freelancer_id=offer.freelancer.id)


########################################################################################################################
# OFFER DELETE
########################################################################################################################
# FREELANCER DELETE
# An offer can be discarded if and only if it is in the "Pending" stage.
@login_required
def freelancer_discard_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    if offer.stage == 'Pending':
        offer.stage = 'Discarded'
        offer.save()
        messages.success(request, 'The offer has been successfully discarded.')
    else:
        messages.error(request, 'This offer cannot be discarded.')

    return redirect('orders:freelancer_orders')


# ! edit this function redirct to the order detail page after payment
@login_required
def fake_payment(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    return render(request, 'orders/fake_payment.html', {'offer': offer})
