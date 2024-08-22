from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Account, Freelancer
from support.models import Ticket



# Create your views here.
@login_required
def admin_dashboard(request):
    if request.user.is_superuser:
        return render(request, 'analytics/admin_dashboard.html')
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
