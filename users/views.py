from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import messages

from functools import wraps

from django.contrib.auth.models import User
from course_apps.course_post.models import Post

# private

def _checkAuth(view):
    @wraps(view)
    def check(request, *args, **kargs):
        if not request.user.is_authenticated():
            messages.warning(request, '請先登入呦')
            return redirect ('/')
        if kargs['user_id'] != str(request.user.id):
            messages.warning(request, '權限不符')
            return redirect('/')
        return view(request, kargs['user_id'])
    return check

@_checkAuth
def show (request, user_id):

    user = User.objects.get(id = user_id)
    return render(request, 'users/show.html', locals())

@_checkAuth
def edit (request, user_id):

    User.objects.get(id = user_id)
    return render(request, 'users/edit.html')

@_checkAuth
def update (request, user_id):

    nickname = request.POST.get('nickname', '')
    user = User.objects.get(id = user_id)
    user.profile.nickname = nickname
    user.save() 

    return redirect('/users/{user_id}'.format(user_id = user_id))

@_checkAuth
def course_post (request, user_id):

    posts = Post.objects.filter(user = request.user).order_by('-created_time')
    
    paginator = Paginator(posts, 10) # Show 10 Posts per page

    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    return render(request, 'users/course_post.html', locals())

def login_cancelled (request):
    messages.warning(request, '登入取消呦')
    return redirect('/')