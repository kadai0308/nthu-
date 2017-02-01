from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.contrib import messages

from course.models import Course
from course_comment.models import Comment

import datetime

def index (request):
    # img_url = '/' + Comment.objects.all()[0].score_img.url
    all_comments = Comment.objects.all().order_by('-created_time')
    course_comment = 'focus'

    if not all_comments:
        no_comment = True

    paginator = Paginator(all_comments, 10) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        comments = paginator.page(paginator.num_pages)

    # return render(request, 'course_comment/index.html', {'contacts': contacts})
    return render(request, 'course_comment/index.html', locals())

def new (request):
    if not request.user.is_authenticated():
        messages.warning(request, '請先登入呦')
        return redirect ('/course_comment/')

    return render(request, 'course_comment/new.html')

def create (request):
    if not request.user.is_authenticated():
        return redirect ('/login')

    # get course
    course_no = request.POST['course_no']
    course = Course.objects.get(course_no = course_no)

    title = request.POST['title']
    content = request.POST['content']
    
    anonymous = [False, True]['anonymous' in request.POST]
    score_img = request.FILES['score_img'] if 'score_img' in request.FILES else None

    sweety = request.POST['sweety'] if 'sweety' in request.POST else 0
    cold = request.POST['cold'] if 'cold' in request.POST else 0
    hardness = request.POST['hardness'] if 'hardness' in request.POST else 0


    # create comment of course
    Comment.objects.create(
        title = title,
        content = content,
        anonymous = anonymous,
        course = course,
        user = request.user,
        created_time = str(datetime.datetime.now()),
        sweety = sweety,
        cold = cold,
        hardness =hardness,
        score_img = score_img,
    )

    return redirect ('/course_comment')

def search (request):
    
    course_no = request.POST['course_no']
    all_comments = Comment.objects.filter(course__course_no = course_no)
    course_comment = 'focus'

    if not all_comments:
        no_comment = True

    paginator = Paginator(all_comments, 10) # Show 10 contacts per page

    page = request.GET.get('page', 1)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        comments = paginator.page(paginator.num_pages)

    # return render(request, 'course_comment/index.html', {'contacts': contacts})
    return render(request, 'course_comment/index.html', locals())

def edit (request, id):
    comment = Comment.objects.get(id = id)
    if not request.user.is_authenticated():
        messages.warning(request, '請先登入呦')
        return redirect ('/course_comment/')
    elif request.user.id != comment.user.id:
        messages.warning(request, '權限不符')
        return redirect ('/course_comment/')

    return render(request, 'course_comment/edit.html', locals())

def update(request, id):
    comment = Comment.objects.get(id = id)
    if not request.user.is_authenticated():
        messages.warning(request, '請先登入呦')
        return redirect ('/course_comment/')
    elif request.user.id != comment.user.id:
        messages.warning(request, '權限不符')
        return redirect ('/course_comment/')

    comment.title = request.POST.get('title','')
    comment.content = request.POST.get('content','')
    
    comment.anonymous = [False, True]['anonymous' in request.POST]
    # score_img = request.FILES['score_img'] if 'score_img' in request.FILES else None

    comment.sweety = request.POST.get('sweety', 0)
    comment.cold = request.POST.get('cold', 0)
    comment.hardness = request.POST.get('hardness', 0)

    comment.save()

    return redirect('/users/{}/course_comment'.format(request.user.id))

def delete(request, id):
    comment = Comment.objects.get(id = id)
    if not request.user.is_authenticated():
        messages.warning(request, '請先登入呦')
        return redirect ('/course_comment/')
    elif request.user.id != comment.user.id:
        messages.warning(request, '權限不符')
        return redirect ('/course_comment/')

    comment.delete()

    return redirect('/users/{}/course_comment'.format(request.user.id))


