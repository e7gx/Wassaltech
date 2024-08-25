from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Account, Freelancer
from support.models import Ticket
from django.db.models import Count, Sum, Avg, Q
from orders.models import Order, Offer
from accounts.models import Account, Freelancer
from django.contrib import messages



# Create your views here.
@login_required
def admin_dashboard(request):
    if request.user.is_superuser:

        # Order statistics
        order_stats = Order.objects.aggregate(
            total_orders=Count('id'),
            open_orders=Count('id', filter=Q(status='Open')),
            completed_orders=Count('id', filter=Q(status='Closed'))
        )

        # User statistics
        user_stats = Account.objects.aggregate(
            total_users=Count('id'),
            customers=Count('id', filter=Q(user_type='Customer')),
            freelancers=Count('id', filter=Q(user_type='Freelancer'))
        )
        
        # Freelancer statistics
        freelancer_stats = Freelancer.objects.aggregate(
            avg_rating=Avg('internal_rating'),
            verified_freelancers=Count('id', filter=Q(is_verified=True))
        )
        
        # Offer statistics
        offer_stats = Offer.objects.aggregate(
            total_offers=Count('id'),
            avg_price=Avg('price'),
            total_revenue=Sum('price', filter=Q(stage='Completed'))
        )
        
        context = {
            'order_stats': order_stats,
            'user_stats': user_stats,
            'freelancer_stats': freelancer_stats,
            'offer_stats': offer_stats
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
    
