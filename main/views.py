from django.shortcuts import render

# Create your views here.
def index (request):
    return render(request, 'main/index.html')

def login (request):
    return render(request, 'main/login.html')