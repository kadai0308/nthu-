from django.contrib import messages
from django.contrib.auth.models import User

def fb_login(request):
    fbResp = request.POST.get('nickname', '')
    User.objects.get

