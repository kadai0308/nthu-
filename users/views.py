from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.models import User

def show (request, id):
    if not request.user.is_authenticated():
        return redirect ('/login')

    user = User.objects.get(id = id)
    return render(request, 'users/show.html', locals())


def edit (request, id):
    if not request.user.is_authenticated():
        return redirect ('/login')

    User.objects.get(id = id)
    return render(request, 'users/edit.html')

def update (request, id):
    nickname = request.POST['nickname']
    user = User.objects.get(id = id)
    user.profile.nickname = nickname
    user.save() 

    return redirect('/users/{id}'.format(id = id))

def login_cancelled (request):
    messages.warning(request, '登入取消呦')
    return redirect('/')
