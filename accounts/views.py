from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Max, Min
from orders.models import Offer
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
            phone_number = request.POST.get('phone_number')  # Changed from 'phone'
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            address = request.POST.get('address')

            try:
                with transaction.atomic():
                    user = User.objects.create_user(username=username, email=email, password=password,
                                                    first_name=first_name, last_name=last_name)
                    Account.objects.create(
                        user=user,
                        phone_number=phone_number,
                        address=address,
                        user_type='Customer'
                    )

                login(request, user)
                messages.success(request, 'Account created successfully')
                return redirect('main:index')
            except IntegrityError:
                messages.error(request, 'Account creation failed. Please try a different username or phone number.')

    return render(request, 'accounts/customer_account.html')

def freelancer_account(request):
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if hasattr(user, 'account') and user.account.user_type == 'Freelancer':
                    login(request, user)
                    return redirect('main:index')  # Redirect to freelancer dashboard
                else:
                    messages.error(request, 'Invalid credentials for freelancer account.')
            else:
                messages.error(request, 'Invalid username or password.')

        elif 'signup' in request.POST:
            form = FreelancerSignUpForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        user = form.save()
                        login(request, user)
                        messages.success(request, 'Account created successfully')
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
def profile(request,):
    if request.user.is_authenticated:
        if request.user.account.user_type == 'Customer':
            return render(request, 'accounts/customer_profile.html', {'user': request.user})
        if request.user.account.user_type == 'Freelancer':
            return render(request, 'accounts/freelancer_profile.html', {'user': request.user})
    else:
        return redirect('accounts:login')

@login_required
def freelancer_profile(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    context = {
        'freelancer': freelancer,
    }
    return render(request, 'accounts/customer_view_freelancer.html', context)

def inbox(request):
    return render(request, 'accounts/inbox.html')

@login_required
def profile(request,):
    if request.user.is_authenticated:
        if request.user.account.user_type == 'Customer':
            return render(request, 'accounts/customer_profile.html', {'user': request.user})
        if request.user.account.user_type == 'Freelancer':
            wallet = Offer.objects.all().filter().aggregate(Sum('price'))['price__sum']
            rating = Review.objects.all().filter().aggregate(Avg('rating'))['rating__avg']
            rating_count = Review.objects.all().count()
            orders_count = Offer.objects.all().count()


            context = {
                'rating': rating,
                'rating_count': rating_count,
                'wallet': wallet,
                'user': request.user,
                'orders_count': orders_count,
            }

            return render(request, 'accounts/freelancer_profile.html', context)
    else:
        return redirect('accounts:login')

