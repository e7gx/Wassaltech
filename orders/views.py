from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from notifications.views import NotificationService as sendemail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from payments.models import Payment
from accounts.decorators import user_type_required
from .forms import OrderForm, OfferForm
from reviews.forms import ReviewForm
from .models import Order, OrderImage, OrderVideo, Offer
from accounts.models import Account
from datetime import datetime


########################################################################################################################
# ORDER CRUD
########################################################################################################################
########################################################################################################################
# ORDER CREATE
########################################################################################################################
# CUSTOMER CREATE
@login_required
def create_order(request):
    """
    Create a new order.

    This view handles the creation of a new order, associating it with the customer (current user),
    and allows them to upload images and a video related to the order.

    Parameters:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponse: The response object containing the rendered order form page or a redirect.
    """

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
    """
    Display all orders for the current user (customer).

    Parameters:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponse: The response object containing the rendered customer orders page.
    """

    orders = Order.objects.filter(customer=request.user.account)
    return render(request, 'orders/customer_orders.html', {'orders': orders})


# CUSTOMER READ
# ! edit  this function
@login_required
def order_history(request):
    """
    Display the order history for the current user.

    This view displays completed and canceled orders for both customers and freelancers.

    Parameters:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponse: The response object containing the rendered order history page.
    """

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
    """
    Display all orders available for freelancers.

    This view displays orders with the status 'Open' that are not already associated with the current freelancer.

    Parameters:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponse: The response object containing the rendered freelancer orders page.
    """

    freelancer = request.user.freelancer
    orders = Order.objects.filter(status='Open').exclude(Q(offer__freelancer=freelancer) & Q(offer__stage='Pending'))
    return render(request, 'orders/freelancer_orders.html', {'orders': orders})


# MUTUAL READ
@login_required
def order_detail(request, order_id):
    """
    Display the details of a specific order.

    This view shows the details of an order, including any accepted offer, associated images, and a review form for customers
    to review the freelancer and provide feedback when the order is closed.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        order_id (int): The ID of the order to display.

    Returns:
        HttpResponse: The response object containing the rendered order detail page.
    """

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
    """
    End (or complete) an order.

    This view manages the completion process for an order by the freelancer and the customer.
    Only the relevant party can mark the order as completed (closed) at a given time.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        order_id (int): The ID of the order to end.

    Returns:
        HttpResponse: The response object containing a redirect to the respective orders page.
    """

    order = get_object_or_404(Order, id=order_id)
    offer = Offer.objects.filter(order=order_id, stage='Accepted').first()
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
    """
    Discard an order.

    This view allows a customer to discard an order, provided it is in the 'Open' status.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        order_id (int): The ID of the order to discard.

    Returns:
        HttpResponse: The response object containing a redirect to the customer orders page or a JSON response for error.
    """

    order = get_object_or_404(Order, id=order_id)
    if hasattr(request.user, 'account') and request.user.account == order.customer:
        if order.status == 'Open':
            order.status = 'Discarded'
            order.save()
            messages.success(request, 'The order has been successfully discarded.')
        else:
            messages.error(request, 'This order cannot be discarded as it has already been linked with a freelancer.')
    else:
        return HttpResponseForbidden("You don't have permission to discard this order.")

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
    """
    Create a new offer for an order.

    This view enables freelancers to create new offers for a specific order, provided they are verified and do not have
    a pending offer for the order.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        order_id (int): The ID of the order for which the offer is being created.

    Returns:
        HttpResponse: The response object containing the rendered offer form page or a redirect.
    """

    order = get_object_or_404(Order, id=order_id)
    order_images = OrderImage.objects.filter(order=order)  # Get all images for the order

    freelancer = request.user.freelancer
    ##################
    # Only verified freelancers should be able to make offers
    # if not freelancer.is_verified:
    #     messages.error(request, "Your account is not verified yet. You can't make offers.")
    #     return redirect('accounts:profile')
    ##################
    # Should allow freelancers to submit another offer if their offer gets rejected
    if Offer.objects.filter(order=order, stage='Pending', freelancer=freelancer).exists():
        messages.error(request, "You already have a pending offer for this order.")
        return redirect('orders:freelancer_offers')

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.order = order
            offer.freelancer = freelancer
            offer.save()
            sendemail.notify_new_offer(freelancer , order , offer.price )
            messages.success(request, "Your offer has been submitted successfully.")
            return redirect('orders:freelancer_offers')
    else:
        form = OfferForm()
    return render(request, 'orders/create_offer.html', {'form': form, 'order': order, "order_images": order_images})


########################################################################################################################
# OFFER READ
########################################################################################################################
# CUSTOMER READ
@login_required
def order_offers(request, order_id):
    """
    Display all offers for a specific order.

    This view displays all offers associated with a specific order, including freelancer details.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        order_id (int): The ID of the order for which offers are being displayed.

    Returns:
        HttpResponse: The response object containing the rendered order offers page.
    """

    order = get_object_or_404(Order, id=order_id, customer=request.user.account)
    order_images = OrderImage.objects.filter(order=order)  # Get all images for the order
    offers = Offer.objects.filter(order=order, stage="Pending").select_related('freelancer', 'freelancer__user')

    context = {
        'order': order,
        'offers': offers,
        'order_images': order_images,
    }

    return render(request, 'orders/order_offers.html', context)


# FREELANCER READ
@login_required
def freelancer_offers(request):
    """
    Display all offers made by the current freelancer.

    Parameters:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponse: The response object containing the rendered freelancer offers page.
    """

    offers = Offer.objects.filter(freelancer=request.user.freelancer)
    return render(request, 'orders/freelancer_offers.html', {'offers': offers})


########################################################################################################################
# OFFER UPDATE
########################################################################################################################
# CUSTOMER UPDATE
@login_required
def accept_offer(request, offer_id):
    """
    Accept an offer for an order.

    This view allows a customer to accept an offer for their order, and updates the order and offer statuses accordingly.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        offer_id (int): The ID of the offer to accept.

    Returns:
        HttpResponse: The response object containing a redirect to the order detail page.
    """

    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order
    print(request.user.account)
    print(order.customer)
    print("1")
    if hasattr(request.user, 'account') and request.user.account == order.customer:
        print("2")
        with transaction.atomic():
            print("3")
            try:
                print("4")
                offer.stage = 'Accepted'
                print("5")
                offer.save()
                print("6")
                Payment.objects.create(offer=offer, amount=offer.price)
                print("7")
                order.status = 'In Progress'
                print("8")
                order.assigned_to = offer.freelancer
                print("9")
                order.save()
                print("10")
                Offer.objects.filter(order=order).exclude(id=offer_id).update(stage='Declined')
                print("11")
                sendemail.notify_order_accepted(offer, order)
            except Exception as e:
                print(e)
    else:
        return HttpResponseForbidden("You don't have permission to accept this offer.")

    return redirect('orders:order_detail', order_id=order.id)


# CUSTOMER UPDATE
# An offer can be cancelled if and only if it is in the "Accepted" stage.
@login_required
def customer_cancel_offer(request, offer_id):
    """
    Cancel an accepted offer by the customer.

    This view allows a customer to cancel an offer that is in the 'Accepted' stage and updates the payment refund
    based on the refund policy. The offer's stage will become "Cancelled" and the order status will become "Open"
    and the order will not be assigned to any particular freelancer.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        offer_id (int): The ID of the offer to cancel.

    Returns:
        HttpResponse: The response object containing a redirect to the order detail page or a JSON response for error.
    """

    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order

    if hasattr(request.user, 'account') and request.user.account == order.customer:
        with transaction.atomic():
            try:
                offer.stage = 'Cancelled'
                offer.save()
                offer.payment.customer_cancel_refund()

                order.status = 'Open'
                order.assigned_to = None
                order.save()
            except Exception as e:
                print(e)
    else:
        return HttpResponseForbidden("You don't have permission to cancel this offer.")

    return redirect('orders:order_detail', order_id=order.id)


# FREELANCER UPDATE
# An offer can be cancelled if and only if it is in the "Accepted" stage.
@login_required
def freelancer_cancel_offer(request, offer_id):
    """
    Cancel an accepted offer by the freelancer.

    This view allows a freelancer to cancel an offer that is in the 'Accepted' stage and updates the freelancer's
    internal rating as well as the payment refund based on the refund policy.
    The offer's stage will become "Cancelled" and the order status will become "Open" and the order will not be assigned
    to any particular freelancer.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        offer_id (int): The ID of the offer to cancel.

    Returns:
        HttpResponse: The response object containing a redirect to the freelancer offers page or a JSON response for error.
    """

    offer = get_object_or_404(Offer, id=offer_id)
    order = offer.order
    print(request.user.freelancer)
    print(order.assigned_to)
    print("1")
    if hasattr(request.user, 'freelancer') and request.user.freelancer == order.assigned_to:
        print("2")
        with transaction.atomic():
            print("3")
            try:
                print("4")
                offer.stage = 'Cancelled'
                print("5")
                offer.save()
                print("6")
                offer.payment.freelancer_cancel_payment()
                print("7")
                # offer.freelancer.update_internal_rating()
                print("8")

                order.status = 'Open'
                print("9")
                order.assigned_to = None
                print("10")
                order.save()
                print("11")
            except Exception as e:
                print(e)
    else:
        return HttpResponseForbidden("You don't have permission to cancel this offer.")

    return redirect('orders:freelancer_offers')


########################################################################################################################
# OFFER DELETE
########################################################################################################################
# FREELANCER DELETE
# An offer can be discarded if and only if it is in the "Pending" stage.
@login_required
def freelancer_discard_offer(request, offer_id):
    """
    Discard a pending offer.

    This view allows a freelancer to discard an offer that is in the 'Pending' stage.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        offer_id (int): The ID of the offer to discard.

    Returns:
        HttpResponse: The response object containing a redirect to the freelancer orders page or a JSON response for error.
    """

    offer = get_object_or_404(Offer, id=offer_id)
    if hasattr(request.user, 'freelancer') and request.user.freelancer == offer.freelancer:
        if offer.stage == 'Pending':
            offer.stage = 'Discarded'
            offer.save()
            messages.success(request, 'The offer has been successfully discarded.')
        else:
            messages.error(request, 'This offer cannot be discarded.')
    else:
        return HttpResponseForbidden("You don't have permission to discard this offer.")

    return redirect('orders:freelancer_orders')

@login_required
def process_payments(request):
    Payment.process_payments()
    return redirect('accounts:freelancer_profile', freelancer_id=request.user.freelancer.id)

@login_required
def deposit_payments(request):
    Payment.deposit_payments()
    return redirect('accounts:freelancer_profile', freelancer_id=request.user.freelancer.id)


# ! edit this function redirect to the order detail page after payment
@login_required
def fake_payment(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    return render(request, 'orders/fake_payment.html', {'offer': offer})
