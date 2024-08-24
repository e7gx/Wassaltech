from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Account, Freelancer
from support.models import Ticket
from django.db.models import Count, Sum, Avg, Q
from orders.models import Order, Offer
from accounts.models import Account, Freelancer
from reviews.models import Review
from orders.models import Offer
from support.models import Ticket
# Create your views here.
@login_required
def admin_dashboard(request):
    if request.user.is_superuser:
            In_progress_orders = Order.objects.filter(status='In Progress').count()
            completed_orders = Order.objects.filter(status='Completed').count()
            best_catgorie = Order.objects.filter(status='Completed').values('category').annotate(Count('category')).order_by('-category__count').first()
            if best_catgorie is not None:
                best_catgorie = best_catgorie['category']
            rating = Review.objects.aggregate(Avg('rating'))['rating__avg']
            orders_count = Offer.objects.all().count()
            total_users = Account.objects.all().count()
            wallet = Offer.objects.filter(stage="Accepted", order__status="Completed").all()
            total_wallet = wallet.aggregate(Sum('price'))['price__sum']#! we need to check the wallet of the Project Wassaltech
            total_customers = Account.objects.all().filter(user_type='Customer').count()
            total_freelancers = Account.objects.all().filter(user_type='Freelancer').count()
            total_admins = Account.objects.all().filter(user_type='Admin').count()
            
            total_prices = Offer.objects.all().filter(stage='Completed').aggregate(Sum('price'))['price__sum']
            total_refunds = Offer.objects.all().filter(stage='Completed').aggregate(Sum('refund'))['refund__sum']
            
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
                # 'total_sum_finalized_offers': total_sum_finalized_offers,
                'rating': rating,
                'orders_count': orders_count,
                'best_catgorie': best_catgorie,
                'completed_orders': completed_orders,
                'In_progress_orders': In_progress_orders,
                'user': request.user,
                
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
        context = {'manage_freelancers': manage_freelancers}
        return render(request, 'analytics/admin_check_freelancers.html', context)
    else:
        return redirect('main:index')



#!5555555555555here we stop 
@login_required
def customer_profile(request, pk):
    try:
        user = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return redirect('main:index')
    
    if request.user.is_superuser and request.user.account.user_type == 'Admin':
        return render(request, 'analytics/admin_view_customer_profile.html', {'user': user})
    else:
        return redirect('main:index')
