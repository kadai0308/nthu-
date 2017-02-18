from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.contrib import messages
from django.db.models import Q

from course.models import Course

import json
import requests

def index (request):
    all_courses = Course.objects.order_by('course_no')
    
    return render(request, 'course/index.html', locals())

def show (request):
    pass

def search (request):
    keyword = request.GET.get('keyword', '')
    all_courses = Course.objects.filter(Q(title_tw__icontains = keyword) | Q(teacher__icontains = keyword) | Q(course_no__icontains = keyword))
    all_courses = all_courses.order_by('course_no')

    paginator = Paginator(all_courses, 10) # Show 10 conmment per page

    page = request.GET.get('page', '')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        comments = paginator.page(paginator.num_pages)

    return render(request, 'course/index.html', locals())

def add_course (request):
    urls = ['https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/OPENDATA/open_course_data.json', 'https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/OPENDATA/open_course_data_10510.json']
    # for url in urls:
    #     all_courses = requests.get(url).text
    #     all_courses = json.loads(all_courses)
    #     for course in all_courses:
    #         dep = course['科號'][5:9].replace(' ','')
    #         Course.objects.get_or_create(
    #             course_no = course['科號'],
    #             defaults = {
    #                 'course_no': course['科號'],
    #                 'title_tw': course['課程中文名稱'],
    #                 'title_en': course['課程英文名稱'],
    #                 'credit': course['學分數'],
    #                 'teacher': course['授課教師'],
    #                 'department': dep,
    #             }
    #         )


def uniq(seq):
    seen = dict()
    dep = seq[::2]
    limit = seq[1::2]
    for index, i in enumerate(dep):
        if not i in seen:
            seen[i] = limit[index]
    return seen