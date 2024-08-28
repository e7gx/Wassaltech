from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from notifications.views import NotificationService as sendemail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from payments.models import Payment
from accounts.decorators import user_type_required
from reviews.models import Review
from .forms import OrderForm, OfferForm
from reviews.forms import ReviewForm
from .models import Order, OrderImage, OrderVideo, Offer
from accounts.models import Account
from datetime import datetime
from django.urls import reverse


########################################################################################################################
# ORDER CRUD
########################################################################################################################
########################################################################################################################
# ORDER CREATE
########################################################################################################################
# CUSTOMER CREATE
@login_required
@user_type_required(['Customer'])
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
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user.account
            order.save()

            files = request.FILES.getlist('files')
            for file in files:
                OrderImage.objects.create(order=order, image=file)

            video = request.FILES.get('video')
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
@user_type_required(['Customer'])
def customer_orders(request):
    """
    Display all orders for the current user (customer).

    Parameters:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponse: The response object containing the rendered customer orders page.
    """

    orders = Order.objects.filter(customer=request.user.account, status__in=['Open', 'In Progress']).annotate(
        pending_offers_count=Count('offer', filter=Q(offer__stage='Pending'))
    )
    return render(request, 'orders/customer_orders.html', {'orders': orders})


# CUSTOMER READ
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
        if user.account.user_type == 'Customer':
            orders = Order.objects.filter(
                Q(customer=user.account) & (Q(status='Closed') | Q(status='Discarded'))).order_by('-created_at')
            offers = []
        elif user.account.user_type == 'Freelancer':
            orders = []
            offers = Offer.objects.filter(Q(freelancer=user.freelancer) & (Q(stage='Discarded') | Q(stage='Declined') | Q(stage='Cancelled') | Q(stage='Completed'))).order_by('-created_at')
        else:
            orders = []
            offers = []
        return render(request, 'orders/order_history.html', {'orders': orders, 'offers': offers})
    else:
        messages.error(request, 'You do not have the necessary permissions to view order history.')
        return redirect('main:index')


# FREELANCER READ
@login_required
@user_type_required(['Freelancer'])
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
    pending_offers = Offer.objects.filter(order=order, stage='Pending')
    order_images = OrderImage.objects.filter(order=order)
    order_video = OrderVideo.objects.filter(order=order).first()
    
    review_form = None

    if request.user == order.customer and not order.customer_completed:
        review_form = ReviewForm()

    context = {
        'order': order,
        'offer': offer,
        'pending_offers': pending_offers,
        'review_form': review_form,
        'order_images': order_images,
        'order_video': order_video,
    }
    return render(request, 'orders/order_detail.html', context)


########################################################################################################################
# ORDER UPDATE
########################################################################################################################
# MUTUAL UPDATE
from django.utils import timezone

@login_required
def end_order(request, order_id):
    """
    End (or complete) an order and submit a review.

    This view manages the completion process for an order by the freelancer and the customer,
    as well as handling the review submission.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        order_id (int): The ID of the order to end.

    Returns:
        HttpResponse: The response object containing a redirect to the respective orders page.
    """
    
    order = get_object_or_404(Order, id=order_id)
    offer = Offer.objects.filter(order=order_id, stage='Accepted').first()
    if request.method == 'POST':
        if hasattr(request.user, 'freelancer') and request.user.freelancer == order.assigned_to:
            order.freelancer_completed = True
            order.save()
            messages.success(request, 'You have successfully marked the order as closed. The customer can now finalize the order.')

        elif hasattr(request.user, 'account') and request.user.account == order.customer:
            if order.freelancer_completed:
                # Handle the review submission
                rating = request.POST.get('rating')
                comment = request.POST.get('comment')

                if rating:
                    review = Review.objects.create(
                        offer=offer,
                        rating=rating,
                        comment=comment,
                        created_at=timezone.now()
                    )
                    
                    order.customer_completed = True
                    order.status = 'Closed'
                    order.save()
                    
                    offer.stage = 'Completed'
                    
                    # Logic for complete on time
                    complete_on_time = (offer.proposed_service_date - timezone.now().date()).days >= 0
                    if complete_on_time:
                        offer.complete_on_time = True
                    
                    offer.save()
                    offer.freelancer.update_internal_rating()
                    messages.success(request, 'You have successfully submitted the review and closed the order.')
                else:
                    messages.error(request, 'Rating is required to close the order.')

            else:
                messages.error(request, 'The freelancer must close the order before you can finalize it.')

        # Redirect based on user type
        if request.user.account.user_type == 'Customer':
            return redirect('orders:customer_orders')
        else:
            return redirect('orders:freelancer_orders')

    return render(request, 'orders/order_detail.html', {'order': order, 'offer': offer})



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
            Offer.objects.filter(order=order, stage="Pending").update(stage='Declined')
            messages.success(request, 'The order has been successfully discarded.')
        else:
            messages.error(request, 'This order cannot be discarded as it has already been linked with a freelancer.')
    else:
        return messages.error(request, "You don't have permission to discard this order.")

    return redirect('orders:customer_orders')


########################################################################################################################
# OFFER CRUD
########################################################################################################################
########################################################################################################################
# OFFER CREATE
########################################################################################################################
# FREELANCER CREATE
@login_required
@user_type_required(['Freelancer'])
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
    order_images = OrderImage.objects.filter(order=order)

    if not hasattr(request.user, 'freelancer'):
        messages.error(request, "You do not have permission to create offers.")
        return redirect('main:index')

    freelancer = request.user.freelancer
    ##################
    # Only verified freelancers should be able to make offers
    if not freelancer.is_verified:
        messages.error(request, "Your account is not verified yet. You can't make offers.")
        return redirect('accounts:profile')
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
            sendemail.notify_new_offer(freelancer, order, price=offer.price)
            offer.save()

            messages.success(request, "Your offer has been submitted successfully.")

            return redirect('orders:order_detail', order_id=order.id,)
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
    # offers = Offer.objects.filter(order=order, stage="Pending").select_related('freelancer', 'freelancer__user')
    offers = Offer.objects.filter(order=order, stage="Pending").select_related('freelancer', 'freelancer__user').order_by('-freelancer__internal_rating')

    context = {
        'order': order,
        'offers': offers,
        'order_images': order_images,
    }

    return render(request, 'orders/order_offers.html', context)


# FREELANCER READ
@login_required
@user_type_required(['Freelancer'])
def freelancer_offers(request):
    """
    Display all offers made by the current freelancer.

    Parameters:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponse: The response object containing the rendered freelancer offers page.
    """

    if hasattr(request.user, 'freelancer'):
        offers = Offer.objects.filter(Q(freelancer=request.user.freelancer) & (Q(stage="Pending") | Q(stage="Accepted")))
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

    if hasattr(request.user, 'account') and request.user.account == order.customer:

        with transaction.atomic():

            try:

                offer.stage = 'Accepted'

                offer.save()

                Payment.objects.create(offer=offer, amount=offer.price)

                order.status = 'In Progress'

                order.assigned_to = offer.freelancer

                order.save()

                Offer.objects.filter(order=order, stage="Pending").exclude(id=offer_id).update(stage='Declined')

                sendemail.notify_order_accepted(offer, order)
            except Exception as e:
                print(e)
    else:
        return messages.error(request, "You don't have permission to accept this offer.")

    return redirect('orders:order_detail', order_id=order.id)


# CUSTOMER UPDATE
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
                sendemail.notify_cancel_offer(offer , order)
            except Exception as e:
                print(e)
    else:
        return messages.error(request, "You don't have permission to cancel this offer.")

    return redirect('orders:order_detail', order_id=order.id)


# FREELANCER UPDATE
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

    if hasattr(request.user, 'freelancer') and request.user.freelancer == order.assigned_to:

        with transaction.atomic():

            try:

                offer.stage = 'Cancelled'

                offer.save()

                offer.payment.freelancer_cancel_payment()

                order.status = 'Open'

                order.assigned_to = None

                order.save()

                offer.freelancer.update_internal_rating()

            except Exception as e:
                print(e)
    else:
        return messages.error(request, "You don't have permission to cancel this offer.")

    return redirect('orders:freelancer_offers')


########################################################################################################################
# OFFER DELETE
########################################################################################################################
# FREELANCER DELETE
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
        return messages.error(request, "You don't have permission to discard this offer.")

    return redirect('orders:freelancer_orders')



# ! edit this function redirect to the order detail page after payment

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
