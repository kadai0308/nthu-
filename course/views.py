from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.contrib import messages
from django.db.models import Q
from django.db.models import Avg
from django.http import JsonResponse

from course.models import Course

import json
import requests
from bs4 import BeautifulSoup
import re

def index (request):
    all_courses = Course.objects.order_by('course_no')
    
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
    print(ACIXSTORE)

    url = 'https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/8/R/6.3/JH8R63002.php?ACIXSTORE={}'.format(ACIXSTORE)
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    main_sheet = soup.find_all('table')[1]
    for i in main_sheet.find_all('tr')[1:]:
        try:
            if '成績未到' in i.find_all('td')[5].text:
                continue

            year = i.find_all('td')[0].text
            semester = i.find_all('td')[1].text
            course_no = i.find_all('td')[2].text.replace('\xa0', '').replace(' ','%20')

            c_key = year+semester+course_no

            score_range_url = ('https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/8/8.3/8.3.3/JH83302.php?'
                'ACIXSTORE={}&'
                'c_key={}').format(ACIXSTORE, c_key)
            
            score_range_html = requests.get(score_range_url).content

            score_range_soup = BeautifulSoup(score_range_html, 'html.parser')

            score_range_data = score_range_soup.find_all('tr')[2].text
            score_range_data_list = score_range_data.replace('\xa0', '').replace(' ','').split('\n')[2:]

            course_no = course_no.replace('%20', ' ')

            print (score_range_soup.find('b'))
            
            print (course.title_tw, course.teacher)
            print ('-'*100)
        except  Exception as e:
            print (str(e))
            continue

    return JsonResponse('success', safe = False)

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


# def uniq(seq):
#     seen = dict()
#     dep = seq[::2]
#     limit = seq[1::2]
#     for index, i in enumerate(dep):
#         if not i in seen:
#             seen[i] = limit[index]
#     return seen


# def course_comment_ajax (request, course_id):
#     course = Course.objects.get(id = course_id)
#     comments = course.comment_set.all()

#     index = request.GET.get('index', '')

#     return 


