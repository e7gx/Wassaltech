from django.shortcuts import render


# Create your views here.

def index(request):
    return render(request, 'main/index.html')
def about(request):
    return render(request , 'main/about.html')
def terms_of_use(request):
    return render(request , 'main/terms_of_use.html')