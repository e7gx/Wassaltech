from decimal import Decimal, ROUND_HALF_UP

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
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('main:index')

    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if hasattr(user, 'account') and user.account.user_type == 'Customer':
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('main:index')
                else:
                    messages.error(request, 'This account is not registered as a customer.')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')

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
                messages.success(request, f'Welcome to Wassaltech, {user.first_name}! Your account has been created successfully.')
                return redirect('main:index')
            except IntegrityError:
                messages.error(request, 'Account creation failed. Please try a different username or phone number.')

    return render(request, 'accounts/customer_account.html')


def freelancer_account(request):
    form = FreelancerSignUpForm()
    if request.user.is_authenticated:
        if request.user.is_superuser:
            messages.info(request, 'You are already logged in as an admin.')
            return redirect('analytics:dashboard')
        else:
            messages.info(request, 'You are already logged in.')
            return redirect('main:index')

    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    messages.success(request, 'Logged in successfully as Admin.')
                    return redirect('analytics:dashboard')
                elif hasattr(user, 'account') and user.account.user_type == 'Freelancer':
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('main:index')
                else:
                    messages.error(request, 'This account is not registered as a freelancer or admin.')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')

        elif 'signup' in request.POST:
            form = FreelancerSignUpForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        user = form.save()
                        login(request, user)
                        messages.success(request, f'Welcome to Wassaltech, {user.first_name}! Your freelancer account has been created successfully.')
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
    if request.user.is_authenticated:
        messages.success(request, 'You have been logged out successfully.')
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
            total_amount_pending_deposit = Payment.objects.filter(Q(offer__freelancer=request.user.freelancer) & (Q(status='Processing') | Q(status='Processed'))).aggregate(total_amount=Sum('amount'))['total_amount']
            total_amount_deposited = Payment.objects.filter(Q(offer__freelancer=request.user.freelancer) & Q(status='Deposited')).aggregate(total_amount=Sum('amount'))['total_amount']
            total_amount_pending_deposit = Decimal(total_amount_pending_deposit or 0)
            total_amount_deposited = Decimal(total_amount_deposited or 0)
            freelancer_wallet_pending = (total_amount_pending_deposit * Decimal(0.9)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            freelancer_wallet = (total_amount_deposited * Decimal(0.9)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

            orders_in_progress = Order.objects.filter(assigned_to=request.user.freelancer, status='In Progress').count()
            orders_completed = Order.objects.filter(assigned_to=request.user.freelancer, status='Closed').count()


            best_catgorie = Order.objects.filter(assigned_to=request.user.freelancer, status='Closed').values('category').annotate(Count('category')).order_by('-category__count').first()

            if best_catgorie is not None:
                best_catgorie = best_catgorie['category']


            rating = Review.objects.filter(offer__freelancer=request.user.freelancer).aggregate(avg_rating=Avg('rating'))['avg_rating']
            rating_count = Review.objects.filter(offer__freelancer=request.user.freelancer).count()
            orders_count = Offer.objects.filter(freelancer=request.user.freelancer).count()



            context = {
                'freelancer_wallet_pending': freelancer_wallet_pending,
                'freelancer_wallet': freelancer_wallet,
                'orders_in_progress': orders_in_progress,
                'orders_completed': orders_completed,
                'best_catgorie': best_catgorie,
                'rating': rating,
                'rating_count': rating_count,
                'orders_count': orders_count,
            }
            return render(request, 'accounts/freelancer_profile.html', context)
        else:
            messages.error(request, 'You do not have permission to view this profile.')
            return redirect('main:index')
    else:
        messages.error(request, 'You need to be logged in to view this profile.')
        return redirect('main:index')


@login_required
def customer_view_profile(request):
    if request.user.is_authenticated:
        if request.user.account.user_type == 'Customer':
            return render(request, 'accounts/customer_profile.html', {'user': request.user})
        else:
            messages.error(request, 'You do not have permission to view this profile.')
            return redirect('main:index')
    else:
        messages.error(request, 'You need to be logged in to view this profile.')
        return redirect('main:index')


@login_required
def freelancer_profile(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    best_catgorie = Order.objects.filter(status='Closed', assigned_to=freelancer).values('category').annotate(Count('category')).order_by('-category__count').first()
    if best_catgorie is not None:
        best_catgorie = best_catgorie['category']
    else:
        best_catgorie = 'لايوجد'
    orders_in_progress = Order.objects.filter(assigned_to=freelancer, status='In Progress').count()
    rating_count = Review.objects.filter(offer__freelancer=freelancer).count()
    rating = Review.objects.filter(offer__freelancer=freelancer).aggregate(avg_rating=Avg('rating'))[
        'avg_rating']

    context = {
        'rating': rating,
        'rating_count': rating_count,
        'orders_in_progress': orders_in_progress,
        'best_catgorie': best_catgorie,
        'freelancer': freelancer,
    }
    return render(request, 'accounts/customer_view_freelancer.html', context)

@login_required
def inbox(request):
    return render(request, 'accounts/inbox.html')

@login_required
def Edit_Profile(request , user_id):
    if request.method == 'POST':
        user = User.objects.get(pk = user_id)
        account = Account.objects.get(user = user)
        user.first_name = request.POST.get('first_name' , user.first_name)
        user.last_name = request.POST.get('last_namr' , user.last_name)
        user.email = request.POST.get('email' , user.email)
        user.username = request.POST.get('username', user.username)
        account.phone_number = request.POST.get('phone_number' , account.phone_number)
        account.address = request.POST.get('address' , account.address)
        user.save()
        account.save()
        return redirect('accounts:customer_view_profile')
    return redirect('accounts:customer_view_profile')
        
        