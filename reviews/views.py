from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm
from orders.models import Order
from django.contrib import messages

@login_required
def submit_review(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST' and request.user == order.customer.user:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.save()
    return redirect('orders:order_detail', order_id=order.id)
