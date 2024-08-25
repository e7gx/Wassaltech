from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from notifications.views import NotificationService as sendemail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import user_type_required
from accounts.models import Account
from reviews.forms import ReviewForm
from .models import Order, OrderImage, OrderVideo, Offer
from .forms import OrderForm, OfferForm
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

            messages.success(request, 'Your order has been created successfully.')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'There was an error creating your order. Please check the form and try again.')
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})


########################################################################################################################
# ORDER READ
########################################################################################################################
# CUSTOMER READ
@login_required
def customer_orders(request):
    orders = Order.objects.filter(customer=request.user.account, status__in=['Open', 'In Progress'])
    for order in orders:
        pending_offers = Offer.objects.filter(order=order, stage='Pending').count()
        order.pending_offers = pending_offers
    return render(request, 'orders/customer_orders.html', {'orders': orders})


# CUSTOMER READ
@login_required
def order_history(request):
    user = request.user
    if hasattr(user, 'account'):
        if user.account.user_type == 'Customer':
            orders = Order.objects.filter(customer=user.account, status='Completed')
        elif user.account.user_type == 'Freelancer':
            orders = Order.objects.filter(assigned_to=user.freelancer, status='Completed')
        else:
            orders = []
        return render(request, 'orders/order_history.html', {'orders': orders})
    else:
        messages.error(request, 'You do not have the necessary permissions to view order history.')
        return redirect('main:index')


# FREELANCER READ
@login_required
def freelancer_orders(request):
    if hasattr(request.user, 'freelancer'):
        freelancer = request.user.freelancer
        orders = Order.objects.filter(status='Open')
        orders = orders.exclude(offer__freelancer=freelancer)
        return render(request, 'orders/freelancer_orders.html', {'orders': orders})
    else:
        messages.error(request, 'You do not have the necessary permissions to view available orders.')
        return redirect('main:index')


# MUTUAL READ
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    offer = Offer.objects.filter(order=order, stage='Accepted').first()
    order_images = OrderImage.objects.filter(order=order)
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

    if request.user.account.user_type == 'Freelancer':
        order.freelancer_completed = True
        order.save()
        messages.success(request, 'You have successfully marked the order as completed. The customer can now finalize the order.')
    elif request.user.account.user_type == 'Customer':
        if order.freelancer_completed:
            order.customer_completed = True
            order.status = 'Completed'
            order.save()
            messages.success(request, 'You have successfully completed the order.')
        else:
            messages.error(request, 'The freelancer must complete the order before you can finalize it.')

    if request.user.account.user_type == 'Customer':
        return redirect('orders:customer_orders')
    else:
        return redirect('orders:freelancer_orders')


########################################################################################################################
# ORDER DELETE
########################################################################################################################
# CUSTOMER DELETE
@login_required
def discard_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not order.offer_set.exists():
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
    order_images = OrderImage.objects.filter(order=order)

    if not hasattr(request.user, 'freelancer'):
        messages.error(request, "You do not have permission to create offers.")
        return redirect('main:index')

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
            sendemail.notify_new_offer(freelancer, order, offer.price)
            messages.success(request, "Your offer has been submitted successfully.")
            return redirect('orders:freelancer_orders')
        else:
            messages.error(request, "There was an error submitting your offer. Please check the form and try again.")
    else:
        form = OfferForm()
    return render(request, 'orders/create_offer.html', {'form': form, 'order': order, "order_images": order_images})


########################################################################################################################
# OFFER READ
########################################################################################################################
# CUSTOMER READ
@login_required
def order_offers(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.account)
    order_images = OrderImage.objects.filter(order=order)
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
    if hasattr(request.user, 'freelancer'):
        offers = Offer.objects.filter(freelancer=request.user.freelancer)
        return render(request, 'orders/freelancer_offers.html', {'offers': offers})
    else:
        messages.error(request, "You do not have permission to view offers.")
        return redirect('main:index')


########################################################################################################################
# OFFER UPDATE
########################################################################################################################
# CUSTOMER UPDATE
@login_required
def accept_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if request.user.account != order.customer:
        messages.error(request, "You don't have permission to accept this offer.")
        return redirect('main:index')

    offer.stage = 'Accepted'
    offer.save()
    unaccepted_offers = Offer.objects.filter(order=order).exclude(id=offer_id)
    for unaccepted_offer in unaccepted_offers:
        unaccepted_offer.stage = 'Declined'
        unaccepted_offer.save()

    order.status = 'In Progress'
    order.assigned_to = offer.freelancer
    order.save()
    sendemail.notify_order_accepted(offer, order)
    messages.success(request, "The offer has been accepted successfully.")
    return redirect('orders:order_detail', order_id=order.id)


# CUSTOMER UPDATE
@login_required
def customer_cancel_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if request.user.account != order.customer:
        messages.error(request, "You don't have permission to cancel this offer.")
        return redirect('main:index')

    full_refund = timedelta(hours=24)
    half_refund = timedelta(hours=12)
    time_until_visit = offer.appointment - datetime.now()
    try:
        if time_until_visit >= full_refund:
            offer.refund = offer.price
            offer.price = 0
            messages.info(request, "You will receive a full refund.")
        elif time_until_visit >= half_refund:
            offer.refund = offer.price / 2
            offer.price = offer.price / 2
            messages.info(request, "You will receive a 50% refund.")
        else:
            messages.info(request, "No refund will be issued due to short notice cancellation.")

        offer.stage = 'Cancelled'
        offer.save()

        order.status = 'Open'
        order.assigned_to = None
        order.save()
        messages.success(request, "The offer has been cancelled successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred while cancelling the offer: {str(e)}")

    return redirect('orders:order_detail', order_id=order.id)


# FREELANCER UPDATE
@login_required
def freelancer_cancel_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if request.user.account != order.assigned_to:
        messages.error(request, "You don't have permission to cancel this offer.")
        return redirect('main:index')
    try:
        offer.stage = 'Cancelled'
        offer.refund = offer.price
        offer.price = 0
        offer.save()
        offer.freelancer.update_internal_rating()

        order.status = 'Open'
        order.assigned_to = None
        order.save()
        messages.success(request, "The offer has been cancelled successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred while cancelling the offer: {str(e)}")

    return redirect('orders:freelancer_offers')


########################################################################################################################
# OFFER DELETE
########################################################################################################################
# FREELANCER DELETE
@login_required
def freelancer_discard_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    if offer.stage == 'Pending':
        offer.stage = 'Discarded'
        offer.save()
        messages.success(request, 'The offer has been successfully discarded.')
    else:
        messages.error(request, 'This offer cannot be discarded as it is no longer in the pending stage.')

    return redirect('orders:freelancer_orders')


@login_required
def fake_payment(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    return render(request, 'orders/fake_payment.html', {'offer': offer})

@login_required
def export_pdf_from_html(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    offer = get_object_or_404(Offer, order=order, stage='Accepted')
    
    customer = order.customer
    customer_user = customer.user if customer else None
    freelancer = offer.freelancer
    freelancer_user = freelancer.user if freelancer else None
    
    context = {
        'order': order,
        'customer_name': f"{customer_user.first_name} {customer_user.last_name}" if customer_user else "N/A",
        'freelancer_name': f"{freelancer_user.first_name} {freelancer_user.last_name}" if freelancer_user else "N/A",
        'freelancer_certificate': freelancer.certificate_id if freelancer else "N/A",
        'order_date': datetime.now().strftime("%Y-%m-%d"),
        'order_category': order.category,
        'order_description': order.issue_description,
        'customer_phone_number': customer.phone_number if customer else "N/A",
        'customer_email': customer_user.email if customer_user else "N/A",
        'freelancer_phone_number': freelancer.user.account.phone_number if freelancer and freelancer.user and hasattr(freelancer.user, 'account') else "N/A",
        'freelancer_email': freelancer_user.email if freelancer_user else "N/A",
        'freelancer_address': freelancer.user.account.address if freelancer and freelancer.user and hasattr(freelancer.user, 'account') else "N/A",
        'customer_address': customer.address if customer else "N/A",
    }
    
    return render(request, 'orders/export_pdf_from_html.html', context)
