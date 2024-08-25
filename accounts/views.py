from django.db import transaction, IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Max, Min, Q
from orders.models import Offer, Order
from payments.models import Payment
from reviews.models import Review
from .forms import FreelancerSignUpForm
from .models import Account, Freelancer
from django.contrib.auth.decorators import login_required


def customer_account(request):
    # if there is a user, redirect to main page
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if hasattr(user, 'account') and user.account.user_type == 'Customer':
                    login(request, user)
                    return redirect('main:index')  # Redirect to customer dashboard
                else:
                    messages.error(request, 'Invalid credentials for customer account.')
            else:
                messages.error(request, 'Invalid username or password.')

        elif 'signup' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            address = request.POST.get('address')
            avatar = request.FILES.get('avatar')

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    Account.objects.create(
                        user=user,
                        phone_number=phone_number,
                        address=address,
                        user_type='Customer',
                        avatar=avatar
                    )

                login(request, user)
                messages.success(request, 'Account created successfully')
                return redirect('main:index')
            except IntegrityError:
                messages.error(request, 'Account creation failed. Please try a different username or phone number.')

    return render(request, 'accounts/customer_account.html')


def freelancer_account(request):
    form = FreelancerSignUpForm()
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('analytics:dashboard')  #! Redirect to the admin page we need to change this
        else:
            return redirect('main:index')

    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                #! Check if the user "user_type" is an Admin
                if user.is_superuser:
                    login(request, user)
                    messages.success(request, 'Logged in as Admin.')
                    return redirect('analytics:dashboard')  #! Redirect to the admin page we need to change this

                #! Check if the user is a Freelancer
                elif hasattr(user, 'account') and user.account.user_type == 'Freelancer':
                    login(request, user)
                    messages.success(request, 'Logged in as Freelancer.')
                    return redirect('main:index')  #! Redirect to freelancer dashboard

                else:
                    messages.error(request, 'Invalid credentials for freelancer or admin account.')
            else:
                messages.error(request, 'Invalid username or password.')

        elif 'signup' in request.POST:
            form = FreelancerSignUpForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        user = form.save()
                        login(request, user)
                        messages.success(request, 'Account created successfully.')
                        return redirect('main:index')
                except IntegrityError:
                    messages.error(request, 'Account creation failed. Please try a different username or phone number.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    else:
        form = FreelancerSignUpForm()

    return render(request, 'accounts/freelancer_account.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('main:index')

@login_required
def freelancer_view_profile(request):
    """
    View function to display the profile of a freelancer user.

    This function calculates various statistics about the freelancer's performance,
    such as total unclaimed and deposited amounts, orders in progress and completed,
    best category, average rating, rating count, and total orders count. It then renders
    the profile page with these statistics.

    Parameters:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponse: The response object containing the rendered profile page or a redirect.
    """
    if request.user.is_authenticated:
        if request.user.account.user_type == 'Freelancer':
            total_amount_unclaimed = Payment.objects.filter(Q(offer__freelancer=request.user) & (Q(status='Processing') | Q(status='Processed'))).aggregate(total_amount=Sum('amount'))['total_amount']
            total_amount_deposited = Payment.objects.filter(Q(offer__freelancer=request.user) & Q(status='Deposited')).aggregate(total_amount=Sum('amount'))['total_amount']
            orders_in_progress = Order.objects.filter(freelancer=request.user, status='In Progress').count()
            orders_completed = Order.objects.filter(freelancer=request.user, status='Completed').count()
            best_catgorie = Order.objects.filter(freelancer=request.user, status='Completed').values('category').annotate(Count('category')).order_by('-category__count').first()
            if best_catgorie is not None:
                best_catgorie = best_catgorie['category']
            rating = Review.objects.filter(freelancer=request.user).aggregate(avg_rating=Avg('rating'))['avg_rating']
            rating_count = Review.objects.filter(freelancer=request.user).count()
            orders_count = Offer.objects.filter(freelancer=request.user).count()
            context = {
                'total_amount_unclaimed': total_amount_unclaimed,
                'total_amount_deposited': total_amount_deposited,
                'orders_in_progress': orders_in_progress,
                'orders_completed': orders_completed,
                'best_catgorie': best_catgorie,
                'rating': rating,
                'rating_count': rating_count,
                'orders_count': orders_count,
                'user': request.user,
            }
            # total_sum_finalized_offers = Offer.objects.filter(stage='Finalized').aggregate(total_price=Sum('price'))['total_price']
            # In_progress_orders = Order.objects.filter(status='In Progress').count()
            # completed_orders = Order.objects.filter(status='Completed').count()
            # best_catgorie = Order.objects.filter(status='Completed').values('category').annotate(Count('category')).order_by('-category__count').first()
            # if best_catgorie is not None:
            #     best_catgorie = best_catgorie['category']
            # rating = Review.objects.aggregate(Avg('rating'))['rating__avg']
            # rating_count = Review.objects.all().count()
            # orders_count = Offer.objects.all().count()
            #
            # context = {
            # 'total_sum_finalized_offers': total_sum_finalized_offers,
            # 'rating': rating,
            # 'rating_count': rating_count,
            # 'orders_count': orders_count,
            # 'best_catgorie': best_catgorie,
            # 'completed_orders': completed_orders,
            # 'In_progress_orders': In_progress_orders,
            # 'user': request.user,
            # }
            return render(request, 'accounts/freelancer_profile.html', context)
        else:
            return redirect('main:index')
    else:
        return redirect('main:index')


@login_required
def customer_view_profile(request):
    if request.user.is_authenticated:
        if request.user.account.user_type == 'Customer':
            return render(request, 'accounts/customer_profile.html', {'user': request.user})
        else:
            return redirect('main:index')
    else:
        return redirect('main:index')



@login_required
def freelancer_profile(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    best_catgorie = Order.objects.filter(status='Finalized').values('category').annotate(Count('category')).order_by('-category__count').first()
    if best_catgorie is not None:
        best_catgorie = best_catgorie['category']

    else:
        best_catgorie = 'لايوجد'
    In_progress_orders = Order.objects.filter(status='In Progress').count()
    rating_count = Review.objects.all().count()
    rating = Review.objects.aggregate(Avg('rating'))['rating__avg']



    context = {
        'rating':rating,
        'rating_count': rating_count,
        'In_progress_orders': In_progress_orders,
        'best_catgorie': best_catgorie,
        'freelancer': freelancer,
    }
    return render(request, 'accounts/customer_view_freelancer.html', context)

def inbox(request):
    return render(request, 'accounts/inbox.html')



