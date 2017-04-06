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

def index (request):
    all_courses = Course.objects.order_by('department')
    
    paginator = Paginator(all_courses, 10) # Show 10 post per page

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
    

def show (request, course_id):
    course = Course.objects.get(id = course_id)
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
        course_score_range = course.coursebyyear_set.filter(scoredistribution__isnull = False).exists()

    return render(request, 'course_page/show.html', locals())

def search (request):
    keyword = request.GET.get('keyword', '')
    all_courses = Course.objects.filter(Q(title_tw__icontains = keyword) | Q(teacher__icontains = keyword) | Q(course_no__icontains = keyword))
    all_courses = all_courses.order_by('course_no')

    paginator = Paginator(all_courses, 10) # Show 10 post per page

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

def import_course_score_range (request):
    ACIXSTORE = request.POST.get('acixstore', '')
    print ('before')
    queue = django_rq.get_queue('high')
    queue.enqueue(import_course_score_range_func, ACIXSTORE, request.user)
    print ('after')
    return redirect('/')

def add_course (request):
    print ('before')
    queue = django_rq.get_queue('high')
    queue.enqueue(add_course_func)
    print ('after')
    return redirect('/')

# def copy_course_data (request):
#     for course in old_course.Course.objects.all():
#         new = new_course.Course.objects.create()
#         new.title_tw = course.title_tw
#         new.title_en = course.title_en
#         new.teacher = course.teacher
#         new.credit = course.credit
#         new.department = course.department
#         new.save()

# def update_course_data(request):
#     for course in Course.objects.all():
#         old = old_course.Course.objects.get(teacher = course.teacher, title_tw = course.title_tw)
#         course.course_no = old.course_no
#         course.save()


# def copy_courseyear_data (request):
#     for data in old_course.CourseByYear.objects.all():
#         new = new_course.CourseByYear.objects.create()
#         new.course_no = data.course_no
#         new.room_and_time = data.room_and_time
#         course_title = data.course.title_tw
#         course_teacher = data.course.teacher
#         a = new_course.Course.objects.filter(title_tw = course_title, teacher = course_teacher)
#         if a.count() > 1:
#             print (a[0].title_tw, a[0].teacher)
#         new.course = new_course.Course.objects.get(title_tw = course_title, teacher = course_teacher)
#         new.save()

def copy_score_data (request):
    for score in old_course.ScoreRange.objects.all():
        new = new_course.ScoreDistribution.objects.create()
        course = new_course.CourseByYear.objects.get(course_no = score.course.course_no)
        new.course = course
        new.score_data = score.score_data
        new.user = score.user
        new.save()
