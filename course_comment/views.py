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
        print (request, args, kargs)
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
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        comments = paginator.page(paginator.num_pages)

    return render(request, 'course_comment/index.html', locals())

@_check_comment_auth
def new (request):

    return render(request, 'course_comment/new.html')

@_check_comment_auth
def create (request):
    
    # get course
    course_no = request.POST.get('course_no', '')

    if course_no == '':
        return redirect(request.META.get('HTTP_REFERER'))

    title = request.POST.get('title', '')
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

    if course_no:
        course = Course.objects.get(course_no = course_no)
        # create comment of course
        Comment.objects.create(
            title = title,
            content = total_content,
            anonymous = anonymous,
            course = course,
            user = request.user,
            created_time = str(datetime.datetime.now()),
            sweety = sweety,
            cold = cold,
            hardness = hardness,
            score_img = score_img,
        )
    else:
        custom_course_name = request.POST.get('custom_course', '')
        # create comment of course
        Comment.objects.create(
            title = title,
            content = content,
            anonymous = anonymous,
            course = None,
            custom_course_name = custom_course_name,
            user = request.user,
            created_time = str(datetime.datetime.now()),
            sweety = sweety,
            cold = cold,
            hardness = hardness,
            score_img = score_img,
        )

    return redirect ('/course_comment')

def search (request):
    # course_no = request.POST.get('course_no', '')
    # all_comments = Comment.objects.filter(course__course_no = course_no)
    
    keyword = request.POST.get('keyword', '')
    courses = Course.objects.filter(Q(title_tw__icontains = keyword) | Q(teacher__icontains = keyword) | Q(course_no__icontains = keyword))
    all_comments = Comment.objects.filter(course__in = courses).order_by('-created_time')
    
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


