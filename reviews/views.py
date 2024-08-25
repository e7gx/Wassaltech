from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from orders.models import Offer, Order
from django.contrib import messages

@login_required
def submit_review(request, order_id):
    """
    Submit a review for an order.

    This view allows customers to submit a review for an order.
    Optionally, it can also close the order if indicated by the form.

    Parameters:
        request (HttpRequest): The request object used to generate this response.
        order_id (int): The ID of the order to review.

    Returns:
        HttpResponse: The response object containing a redirect to the orders history page.
    """

    order = get_object_or_404(Order, id=order_id)
    offer = get_object_or_404(Offer, order=order)

    if request.method == 'POST' and request.user == order.customer.user:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.offer = offer
            review.save()

            if request.POST.get('action') == 'complete':
                order.customer_completed = True
                order.status = 'Closed'
                order.save()
                messages.success(request, 'Review submitted and order completed successfully.')
            else:
                messages.success(request, 'Review submitted successfully.')
        else:
            messages.error(request, 'There was an error with your submission.')

    return redirect('orders:order_history')
