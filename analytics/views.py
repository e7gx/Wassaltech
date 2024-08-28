from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.contrib import messages

from accounts.models import Account, Freelancer
from analytics.forms import PaymentFilterForm
from payments.models import Payment
from support.models import Ticket
from orders.models import Order, Offer
from reviews.models import Review

# Create your views here.
@login_required
def admin_dashboard(request):
    Payment.process_payments()
    if request.user.is_superuser:
        orders_open = Order.objects.filter(status='Open').count()
        orders_in_progress = Order.objects.filter(status='In Progress').count()
        orders_closed = Order.objects.filter(status='Closed').count()
        orders_discarded = Order.objects.filter(status='Discarded').count()
        best_catgorie = Order.objects.filter(status='Closed').values('category').annotate(Count('category')).order_by('-category__count').first()
        if best_catgorie is not None:
            best_catgorie = best_catgorie['category']
        rating = Review.objects.aggregate(Avg('rating'))['rating__avg']
        orders_count = Offer.objects.all().count()
        total_users = Account.objects.all().count()

        # wallet = Offer.objects.filter(stage="Accepted", order__status="Completed").all()
        # total_wallet = wallet.aggregate(Sum('price'))['price__sum']#! we need to check the wallet of the Project Wassaltech
        total_customers = Account.objects.all().filter(user_type='Customer').count()
        total_freelancers = Account.objects.all().filter(user_type='Freelancer').count()
        total_admins = Account.objects.all().filter(user_type='Admin').count()

        # total_amount_pending_deposit = Payment.objects.filter(Q(status='Processing') | Q(status='Processed')).aggregate(
        #     total_amount=Sum('amount'))['total_amount']
        # total_refund_pending_deposit = Payment.objects.filter(Q(status='Processing') | Q(status='Processed')).aggregate(
        #     total_refund_amount=Sum('refund_amount'))['total_refund_amount']
        total_amount_deposited = Payment.objects.filter(Q(status='Deposited')).aggregate(total_amount=Sum('amount'))[
            'total_amount']
        total_refund_deposited = Payment.objects.filter(Q(status='Deposited')).aggregate(total_refund_amount=Sum('refund_amount'))[
            'total_refund_amount']
        total_amount_deposited = Decimal(total_amount_deposited or 0)
        total_refund_deposited = Decimal(total_refund_deposited or 0)

        # Calculate total money flow
        total_money_flow = total_amount_deposited + total_refund_deposited

        # Calculate wallets
        wallet = (total_amount_deposited * Decimal(0.1)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        freelancer_wallet = total_amount_deposited - wallet
        customer_wallet = total_refund_deposited.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        # total_money_flow = total_amount_deposited + total_refund_deposited
        # wallet = (total_amount_deposited * Decimal(0.1)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        # freelancer_wallet = total_amount_deposited - wallet
        # customer_wallet = total_refund_deposited.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        tickets_count = Ticket.objects.all().count()
        ticket_status_count = Ticket.objects.values('ticket_status').annotate(Count('ticket_status')).order_by('-ticket_status__count').first()
        if ticket_status_count is not None:
            ticket_status_count = ticket_status_count['ticket_status']

        tickets_completed = Ticket.objects.all().filter(ticket_status='closed').count()
        tickets_in_progress = Ticket.objects.all().filter(ticket_status='in_progress').count()
        tickets_open = Ticket.objects.all().filter(ticket_status='open').count()

        most_category_tickets = Ticket.objects.values('ticket_category').annotate(Count('ticket_category')).order_by('-ticket_category__count').first()
        if most_category_tickets is not None:
            most_category_tickets = most_category_tickets['ticket_category']

        context = {
            'orders_open': orders_open,
            'orders_in_progress': orders_in_progress,
            'orders_closed': orders_closed,
            'orders_discarded': orders_discarded,
            'best_catgorie': best_catgorie,
            'rating': rating,
            'orders_count': orders_count,
            'total_users': total_users,
            'total_customers': total_customers,
            'total_freelancers': total_freelancers,
            'total_admins': total_admins,
            # 'total_amount_deposited': total_amount_deposited,
            # 'total_refund_deposited': total_refund_deposited,
            'total_money_flow': total_money_flow,
            'wallet': wallet,
            'freelancer_wallet': freelancer_wallet,
            'customer_wallet': customer_wallet,
            'tickets_count': tickets_count,
            'ticket_status_count': ticket_status_count,
            'tickets_completed': tickets_completed,
            'tickets_in_progress': tickets_in_progress,
            'tickets_open': tickets_open,
            'most_category_tickets': most_category_tickets,
            'user': request.user,
        #     'total_wallet': total_wallet,  # Why?
        }
        return render(request, 'analytics/admin_dashboard.html', context)
    else:
        return redirect('main:index')

@login_required
def admin_tickets(request):
    if request.user.is_superuser:
        admin_tickets = Ticket.objects.all()
        context = {'admin_tickets': admin_tickets}
        return render(request, 'analytics/admin_tickets.html', context)
    else:
        return redirect('main:index')


#!5555555555555here we stop
@login_required
def admin_check_customers(request):

    if request.user.is_superuser:
        manage_customers = Account.objects.filter(user_type= 'Customer').all()
        context = {'manage_customers': manage_customers}
        return render(request, 'analytics/admin_check_customers.html', context)
    else:
        return redirect('main:index')

@login_required
def admin_check_freelancers(request):
    if request.user.is_superuser:
        manage_freelancers = Freelancer.objects.all()

        context = {
            'manage_freelancers': manage_freelancers,
            }


        return render(request, 'analytics/admin_check_freelancers.html', context)
    else:
        return redirect('main:index')



@login_required
def customer_profile(request, pk):
    if request.user.is_superuser:
        try:
            customer_profile = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return redirect('main:index')

        if request.user.is_superuser or request.user.account == customer_profile:
            return render(request, 'analytics/admin_view_customer_profile.html', {'customer_profile': customer_profile})
        else:
            return redirect('main:index')


@login_required
def edit_freelancer_profile(request: HttpRequest, pk: int) -> HttpResponse:
    if request.user.is_superuser:
        try:
            freelancer = Freelancer.objects.get(pk=pk)
        except Freelancer.DoesNotExist:
            return redirect('main:index')

        if request.user.is_superuser or request.user.account == freelancer.user:
            if request.method == 'POST':
                is_verified = request.POST.get('is_verified', 'False') == 'True'
                certificate_expiration = request.POST.get('certificate_expiration')

                freelancer.is_verified = is_verified
                freelancer.certificate_expiration = certificate_expiration
                freelancer.save()

                messages.success(request, 'Profile updated successfully!')
                return redirect('analytics:edit_freelancer_profile', pk=freelancer.pk)

            return render(request, 'analytics/edit_freelancer_info.html', {'freelancer': freelancer})
        else:
            return redirect('main:index')



@login_required
def admin_payment(request):
    if request.user.is_superuser:
        Payment.process_payments()
        if request.user.is_superuser:
            form = PaymentFilterForm(request.GET or None)
            payments = Payment.objects.all()

            if form.is_valid():
                status = form.cleaned_data.get('status')
                if status:
                    payments = payments.filter(status=status)

            context = {
                'payments': payments,
                'form': form,
            }
            return render(request, 'analytics/admin_payment.html', context)
        else:
            return redirect('main:index')

# @login_required
# def admin_deposit(request):
#     if request.user.is_superuser:
#         Payment.deposit_payments()
#         return redirect('analytics:admin_payment')
#     else:
#         return redirect('main:index')


@login_required
def admin_deposit_payment(request, pk):
    if request.user.is_superuser:
        payment = get_object_or_404(Payment, pk=pk)
        if payment.status == 'Processed':
            payment.status = 'Deposited'
            payment.deposit_date = datetime.now()
            payment.save()
        return redirect('analytics:admin_payment')
    else:
        return redirect('main:index')