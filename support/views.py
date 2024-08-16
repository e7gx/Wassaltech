from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from support.models import Ticket

@login_required
def create_ticket(request):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':
                new_ticket = Ticket.objects.create(
                    ticket_creator=request.user.account, 
                    ticket_category=request.POST.get('ticket_category'), 
                    ticket_title=request.POST.get('ticket_title'),
                    ticket_description=request.POST.get('ticket_description'),
                    ticket_status=request.POST.get('ticket_status', Ticket.StatusChoices.OPEN),  
                )
                new_ticket.save()
                return HttpResponse('Ticket created successfully')
        except Exception as e:
            print(e)
            
        context = {
            'ticket_categorys': Ticket.TICKET_CATEGORYS,
        }
        
    return render(request, 'support/ticket_form.html', context)

@login_required
def display_tickets(request: HttpRequest):
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser and request.user.is_staff:
                tickets = Ticket.objects.all()
            else:
                
                tickets = Ticket.objects.filter(ticket_creator=request.user.account)
    except:
        print('opss looks like there is an error in display tickets')
        
    return render(request, 'support/display_all_tickets.html', {'tickets': tickets})



@login_required
def display_ticket(request: HttpRequest, ticket_id: int):
    ticket = Ticket.objects.get(id=ticket_id)
    return render(request, 'support/display_ticket.html', {'ticket': ticket})


