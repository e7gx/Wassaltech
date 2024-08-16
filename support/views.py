from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from support.models import Ticket, Comment

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
                return redirect('support:display_tickets')
        except Exception as e:
            print(e)
            
        context = {
            'ticket_categorys': Ticket.TICKET_CATEGORYS,
        }
        
    return render(request, 'support/ticket_form.html', context)



@login_required
def display_tickets(request: HttpRequest):
    '''
    هنا تعرض كامل التذاكر اذا كان مستخدم عادي تعرض له تذاكرة هو فقط 
    اذا كان مدير النظام تعرض له كامل التذاكر
    '''
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
def ticket_detail(request: HttpRequest, ticket_id: int):
    '''
    هذي تعرض كامل التفاصيل الخاصة بالتذاكرة ،وطبعا فيه داخلها التعليقات الخاصة بالمستخدم و ردود المشرفين على التذكرة  
    طبعا اذا احد حاول يدخل الصفحة وهو يعني مو صاحب التذكرة يمنعه ،
    سوي اعادة توجيه للصفحة الي تبغاها بدال مايطلع له رسالة
'''
    if request.user.is_authenticated:
        ticket = Ticket.objects.get(pk=ticket_id)
        ticket_comments = Comment.objects.filter(ticket=ticket)
        if ticket.ticket_creator == request.user.account:
            return render(request, 'support/ticket_detail.html', {'ticket': ticket,'ticket_comments': ticket_comments})
        else:
            return HttpResponse('You are not authorized to view this ticket')#! هنا اقصد
            #! redirect('main:index')
    else:
        return redirect('main:index')


@login_required
def ticket_edit(request, ticket_id):
    '''
    هذا خاص بتعديل التذكرة ،محد يمديه يدخل للفيو هذا الا الادمن والموظفين فقط  
    فيه صلاحيات اكبر من اهمها تعديل الحالة حقت التذكرة 
    
    
    لاتنسى احمد تحذف الكومنتات ذي 
    '''
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect('main:index')

    if ticket.ticket_creator != request.user.account:
        return HttpResponse('You are not authorized to edit this ticket')#! غيرها احمد خليها توديه للصفحة حقت كامل التذاكر

    if request.method == 'POST':
        #! هذي حقت التذاكر اللي تحفظ التغييرات اللي يسويها المستخدم
        if 'ticket_title' in request.POST:
            ticket.ticket_category = request.POST.get('ticket_category')
            ticket.ticket_title = request.POST.get('ticket_title')
            ticket.ticket_description = request.POST.get('ticket_description')
            ticket.ticket_status = request.POST.get('ticket_status')
            ticket.save()
            return redirect('support:display_tickets')
        
        #! هذي تبع الكومينتات اللي يضيفها المستخدم
        elif 'comment_text' in request.POST:
            comment_text = request.POST.get('comment_text')
            if comment_text: 
                Comment.objects.create(
                    ticket=ticket,
                    comment_creator=request.user.account,  #! هذي تع اليوزر اللي يضيف الكومينت
                    comment_text=comment_text
                )
            return redirect('support:ticket_edit', ticket_id=ticket_id)

    comments = ticket.comments.all()
    context = {
        'ticket': ticket,
        'ticket_categorys': Ticket.TICKET_CATEGORYS,
        'ticket_status': Ticket.StatusChoices.choices,
        'comments': comments,
    }
    return render(request, 'support/ticket_edit.html', context)


@login_required
def add_comment(request, ticket_id):
    '''
    هذا خاص بالمستخذم تحديدا عشان يقدر يضيف تعليقات ويعرض تعليقاته في نفس الصحفة ،
    '''
    if request.user.is_authenticated:
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        if request.method == 'POST':
            comment_text = request.POST.get('comment_text')
            if comment_text:  
                Comment.objects.create(
                    ticket=ticket,
                    comment_creator=request.user.account,
                    comment_text=comment_text
                )
        context = {
            'ticket': ticket,
            'comments': ticket.comments.all(),
        }
        return render(request, 'support/comments_page.html', context)
    else:
        return redirect('main:index')