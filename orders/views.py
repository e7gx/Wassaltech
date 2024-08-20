
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from accounts.models import Account
from reviews.forms import ReviewForm
from .models import Order, OrderImage, OrderVideo, Offer
from .forms import OrderForm, OfferForm
from django.contrib import messages
from accounts.decorators import user_type_required
from datetime import datetime, timedelta

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

@login_required
def freelancer_orders(request):
    freelancer = request.user.freelancer
    orders = Order.objects.filter(status='Open')
    orders = orders.exclude(offer__freelancer=freelancer)
    return render(request, 'orders/freelancer_orders.html', {'orders': orders})

@login_required
def create_offer(request, order_id):
    order = get_object_or_404(Order, id=order_id)
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
            messages.success(request, "Your offer has been submitted successfully.")
            return redirect('orders:freelancer_orders')
    else:
        form = OfferForm()
    return render(request, 'orders/create_offer.html', {'form': form, 'order': order})


@login_required
def order_offers(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.account)
    order_images = OrderImage.objects.filter(order=order)  # Get all images for the order
    offers = Offer.objects.filter(order=order).select_related('freelancer', 'freelancer__user')
    
    context= {
        'order': order,
        'offers': offers,
        'order_images': order_images,
    }
    
    return render(request, 'orders/order_offers.html', context)


@login_required
def accept_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if request.user.account != order.customer:
        return HttpResponseForbidden("You don't have permission to accept this offer.")

    offer.status = 'Accepted'
    offer.save()
    # Should set status to declined instead of deleting offers
    unaccepted_offers = Offer.objects.filter(order=order).exclude(id=offer_id)
    for offer in unaccepted_offers:
        offer.status = 'Declined'
        offer.save()
    # Offer.objects.filter(order=order).exclude(id=offer_id).delete()

    order.status = 'In Progress'
    order.assigned_to = offer.freelancer
    order.save()

    return redirect('orders:order_detail', order_id=order.id)

@user_type_required(['Customer'])
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

        offer.status = 'Cancelled'
        offer.save()

        order.status = 'Open'
        order.assigned_to = None
        order.save()
    except Exception as e:
        print(e)

    return redirect('orders:order_detail', order_id=order.id)

@user_type_required(['Freelancer'])
def freelancer_cancel_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if request.user.account != order.assigned_to:
        return HttpResponseForbidden("You don't have permission to cancel this offer.")
    try:
        offer.status = 'Cancelled'
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


#! edit this function redirct to the order detail page after payment
@login_required
def fake_payment(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    return render(request, 'orders/fake_payment.html', {'offer': offer})



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


def end_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user.account.user_type == 'Freelancer':
        order.freelancer_completed = True
        order.save()
        messages.success(request, 'You have successfully marked the order as completed. The customer can now finalize the order.')
    elif request.user.account.user_type == 'Customer':
        if order.freelancer_completed:
            order.customer_completed = True
            order.status = 'Completed'

            # Logic for complete on time

            order.save()
            messages.success(request, 'You have successfully completed the order.')
        else:
            messages.error(request, 'The freelancer must complete the order before you can finalize it.')

    if request.user.account.user_type == 'Customer':
        return redirect('orders:customer_orders')
    else:
        return redirect('orders:freelancer_orders')

#! edit  this function
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

@login_required
def customer_orders(request):
    orders = Order.objects.filter(customer=request.user.account)
    return render(request, 'orders/customer_orders.html', {'orders': orders})

@login_required
def freelancer_offers(request):
    offers = Offer.objects.filter(freelancer=request.user.freelancer)
    return render(request, 'orders/freelancer_offers.html', {'offers': offers})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not order.offer_set.exists():
        order.status = 'Cancelled'
        order.save()
        messages.success(request, 'The order has been successfully cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled as it has already been linked with a freelancer.')

    if request.user.account.user_type == 'Customer':
        return redirect('orders:customer_orders')
    else:
        return redirect('orders:freelancer_orders')
