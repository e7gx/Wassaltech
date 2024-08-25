from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm
from orders.models import Offer
from django.contrib import messages

@login_required
def submit_review(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    if request.method == 'POST' and request.user == offer.customer.user:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.offer = offer 
            review.save()
            messages.success(request, 'Review submitted successfully.')
        else:
            messages.error(request, 'There was an error with your submission.')
    return redirect('orders:order_detail', offer_id=offer.id)
