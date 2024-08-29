from django.shortcuts import render, redirect

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        if request.user.account.user_type != 'Admin':
            return render(request, 'main/index.html')
        else:
            return redirect('analytics:dashboard')
    else:
        return render(request, 'main/index.html')
def about(request):
    return render(request , 'main/about.html')
def terms_of_use(request):
    return render(request , 'main/terms_of_use.html')
def questions(request):
    return render(request , 'main/questions.html')
def cancel(request):
    return render(request , 'main/cancel.html')
def contect(request):
    return render(request , 'main/contect.html')
