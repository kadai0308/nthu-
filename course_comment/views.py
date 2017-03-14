from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.contrib import messages
from functools import wraps
from django.db.models import Q

from course.models import Course
from course_comment.models import Comment

import datetime

# private
def _check_comment_auth(view):
    @wraps(view)
    def check(request, *args, **kargs):
        if not request.user.is_authenticated():
            messages.warning(request, '請先登入呦')
            return redirect ('/')

        if 'comment_id' in kargs:
            comment = Comment.objects.get(id = kargs['comment_id'])
            if comment.user.id != request.user.id:
                messages.warning(request, '權限不符')
                return redirect('/')

            return view(request, comment)

        return view(request)
    
    return check

@_check_comment_auth
def index (request):
    if not request.user.comment_set.exists():
        ban = 'ban'

    all_comments = Comment.objects.all().order_by('-created_time')
    course_comment = 'focus'

    paginator = Paginator(all_comments, 10) # Show 10 conmment per page

    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    return render(request, 'course_comment/index.html', locals())

@_check_comment_auth
def new (request):
    course_id = request.GET.get('course_id', '')
    if course_id:
        course = Course.objects.get(id = int(course_id))

    return render(request, 'course_comment/new.html', locals())

@_check_comment_auth
def create (request):
    
    # get course
    course_id = request.POST.get('course_no', '')

    if course_id == '':
        return redirect(request.META.get('HTTP_REFERER'))

    title = request.POST.get('title', '')
    teacher = request.POST.get('teacher', '')
    scoring = request.POST.get('scoring', '')
    ta = request.POST.get('ta', '')
    content = request.POST.get('content', '')

    total_content = '【評分方式】' + scoring + '\n\n'
    total_content += '【助教表現】' + ta + '\n\n'
    total_content += '【修課心得】' + content + '\n\n'
    
    score_img = request.FILES['score_img'] if 'score_img' in request.FILES else None

    sweety = request.POST['sweety'] if 'sweety' in request.POST else 0
    cold = request.POST['cold'] if 'cold' in request.POST else 0
    hardness = request.POST['hardness'] if 'hardness' in request.POST else 0

    try:
        if course_id:
            course = Course.objects.get(id = course_id)
            # create comment of course
            Comment.objects.create(
                title = title,
                content = total_content,
                anonymous = True,
                course = course,
                user = request.user,
                created_time = str(datetime.datetime.now()),
                sweety = sweety,
                cold = cold,
                hardness = hardness,
                score_img = score_img,
            )
    except  Exception as e: 
        print ('log1:', str(e))
        import sys
        print ('log2:', str(sys.exc_info()))

    return redirect ('/course_comment')

def show (request, comment_id):
    all_comments = [Comment.objects.get(id = comment_id)]
    course_comment = 'focus'
    paginator = Paginator(all_comments, 10) # Show 10 conmment per page

    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)
    return render(request, 'course_comment/index.html', locals())

@_check_comment_auth
def edit (request, comment):
    return render(request, 'course_comment/edit.html', locals())

@_check_comment_auth
def update(request, comment):

    comment.title = request.POST.get('title','')
    comment.content = request.POST.get('content','')

    # score_img = request.FILES['score_img'] if 'score_img' in request.FILES else None

    comment.sweety = request.POST.get('sweety', 0)
    comment.cold = request.POST.get('cold', 0)
    comment.hardness = request.POST.get('hardness', 0)

    comment.save()

    return redirect('/users/{}/course_comment'.format(request.user.id))

@_check_comment_auth
def delete(request, comment):

    comment.delete()

    return redirect('/users/{}/course_comment'.format(request.user.id))

def search (request):
    
    keyword = request.GET.get('keyword', '')
    courses = Course.objects.filter(Q(title_tw__icontains = keyword) | Q(teacher__icontains = keyword) | Q(course_no__icontains = keyword))
    all_comments = Comment.objects.filter(course__in = courses).order_by('-created_time')

    if not all_comments:
        no_comment = True

    paginator = Paginator(all_comments, 10) # Show 10 contacts per page

    page = request.GET.get('page', 1)
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    # return render(request, 'course_comment/index.html', {'contacts': contacts})
    return render(request, 'course_comment/index.html', locals())

