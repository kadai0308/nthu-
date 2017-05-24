from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.contrib import messages
from django.db.models import Q
from django.db.models import Avg
from django.http import JsonResponse

from course_apps.course_page.models import Course, CourseByYear, ScoreDistribution

import course.models as old_course
import course_apps.course_page.models as new_course

import os
from functools import wraps
import json
import requests
from bs4 import BeautifulSoup
import html
import django_rq
from course_apps.course_page.worker import add_course_func


# private
def _check_user_auth(view):
    @wraps(view)
    def check(request, *args, **kargs):
        if not request.user.is_authenticated():
            messages.warning(request, '請先登入呦')
            return redirect ('/')
        return view(request, )
    return check


@_check_user_auth
def index(request):
    all_courses = Course.objects.filter(~Q(latest_open_time='暫無資料')).order_by('-latest_open_time')
    paginator = Paginator(all_courses, 10)  # Show 10 post per page
    page = request.GET.get('page', '')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    return render(request, 'course_page/index.html', locals())


def show(request, course_id):
    course = Course.objects.get(id=course_id)
    posts = course.post_set.all()
    posts_amount = course.post_set.count()

    sweety_average = posts.aggregate(Avg('sweety'))['sweety__avg'] or 0.0
    cold_average = posts.aggregate(Avg('cold'))['cold__avg'] or 0.0
    hardness_average = posts.aggregate(Avg('hardness'))['hardness__avg'] or 0.0
    sweety_average = round(sweety_average, 1)
    cold_average = round(cold_average, 1)
    hardness_average = round(hardness_average, 1)

    if not request.user.is_anonymous:
        user_score_range = request.user.scoredistribution_set.exists()
        course_score_range = course.coursebyyear_set.filter(
            scoredistribution__isnull=False).exists()
    return render(request, 'course_page/show.html', locals())


def search(request):
    keyword = request.GET.get('keyword', '')
    all_courses = Course.objects.filter(Q(title_tw__icontains=keyword) | Q(teacher__icontains=keyword) | Q(course_no__icontains = keyword))
    all_courses = all_courses.order_by('course_no')
    paginator = Paginator(all_courses, 10)  # Show 10 post per page

    page = request.GET.get('page', '')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    return render(request, 'course_page/index.html', locals())


def add_course(request):
    print('before')
    queue = django_rq.get_queue('high')
    queue.enqueue(add_course_func)
    print('after')
    return redirect('/')

# for i in Course.objects.all():
#     if i.coursebyyear_set.exists():
#             course_no = i.coursebyyear_set.order_by('-course_no')[0].course_no
#             s = course_no[:3] + ' '
#             if course_no[3:5] == '10':
#                     s += '上學期'
#             else:
#                     s += '下學期'
#             print(s)
#             i.latest_open_time = s
#             i.save()
#     else:
#             i.latest_open_time = '暫無資料'
#             i.save()











