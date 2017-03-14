from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.contrib import messages
from django.db.models import Q
from django.db.models import Avg
from django.http import JsonResponse

from course.models import Course, CourseByYear, ScoreRange

import os
from functools import wraps
import json
import requests
from bs4 import BeautifulSoup
import html
import django_rq
from course.worker import add_course_func, import_course_score_range_func

def index (request):
    all_courses = Course.objects.order_by('department')
    
    paginator = Paginator(all_courses, 10) # Show 10 comment per page

    page = request.GET.get('page', '')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    return render(request, 'course/index.html', locals())
    

def show (request, course_id):
    course = Course.objects.get(id = course_id)
    comments = course.comment_set.all()
    comments_amount = course.comment_set.count()

    sweety_average = comments.aggregate(Avg('sweety'))['sweety__avg'] or 0.0
    cold_average = comments.aggregate(Avg('cold'))['cold__avg'] or 0.0
    hardness_average = comments.aggregate(Avg('hardness'))['hardness__avg'] or 0.0
    sweety_average = round(sweety_average, 1)
    cold_average = round(cold_average, 1)
    hardness_average = round(hardness_average, 1)

    if not request.user.is_anonymous:
        user_score_range = request.user.scorerange_set.exists()
        course_score_range = course.coursebyyear_set.filter(scorerange__isnull = False).exists()

    return render(request, 'course/show.html', locals())

def search (request):
    keyword = request.GET.get('keyword', '')
    all_courses = Course.objects.filter(Q(title_tw__icontains = keyword) | Q(teacher__icontains = keyword) | Q(course_no__icontains = keyword))
    all_courses = all_courses.order_by('course_no')

    paginator = Paginator(all_courses, 10) # Show 10 comment per page

    page = request.GET.get('page', '')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    return render(request, 'course/index.html', locals())

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

