from django.shortcuts import render
from django.http import HttpResponse

from accounts.models import Freelancer
from support.models import Ticket



# Create your views here.
def admin_dashboard(request):
    return render(request, 'analytics/admin_dashboard.html')


def admin_tickets(request):
    if request.user.is_superuser:
        admin_tickets = Ticket.objects.all()
        context = {'admin_tickets': admin_tickets}
        return render(request, 'analytics/admin_tickets.html', context)
    else:
        return HttpResponse("You are not authorized to view this page")

def admin_check_freelancers(request):
    if request.user.is_superuser:
        manage_freelancers = Freelancer.objects.all()
        context = {'manage_freelancers': manage_freelancers}
        return render(request, 'analytics/admin_check_freelancers.html', context)
    else:
        return HttpResponse("You are not authorized to view this page")




