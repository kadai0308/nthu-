from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import messages

from functools import wraps

from django.contrib.auth.models import User
from course_comment.models import Comment

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
def course_comment (request, user_id):

    user_comments = Comment.objects.filter(user = request.user).order_by('-created_time')
    
    paginator = Paginator(user_comments, 10) # Show 10 conmment per page

    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        comments = paginator.page(paginator.num_pages)

    return render(request, 'users/course_comment.html', locals())

def login_cancelled (request):
    messages.warning(request, '登入取消呦')
    return redirect('/')