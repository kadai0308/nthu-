from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q

from course_apps.course_page.models import Course
from course_apps.course_post.models import Post

import re

def search_course (request):
    keyword = request.GET.get('keyword', '')
    courses = Course.objects.filter(Q(title_tw__icontains = keyword) | Q(teacher__icontains = keyword) | Q(department__icontains = keyword))

    courses = courses.order_by('title_tw')
    for i in courses:
        print (i.course_no)

    data = list()
    for index, course in enumerate(courses):
        # if data and courses[index - 1].title_tw == course.title_tw and courses[index - 1].teacher == course.teacher:
        #     continue

        course_data = dict()
        course_data['title'] = course.title_tw
        course_data['teacher'] = replace(course.teacher)
        course_data['course_no'] = course.course_no
        course_data['course_id'] = course.id
        data.append(course_data)

    # sort by course_no
    data = sorted(data, key = lambda course: course['course_no'][4:])

    response = JsonResponse(data, safe = False)
    return response

def search_post (request):
    course_no = request.GET['course_no']
    posts = post.objects.filter(course__course_no = course_no)

    data = list()

    for post in posts:
        post_data = dict()
        post_data['title'] = post.course.title_tw
        post_data['teacher'] = replace(post.course.teacher)
        post_data['content'] = post.content
        post_data['sweety'] = post.sweety
        post_data['cold'] = post.cold
        post_data['hardness'] = post.hardness
        post_data['user'] = post.user.profile.nickname
        data.append(post_data)

    response = JsonResponse(data, safe = False)
    return response

def score_range (request):
    course_id = request.GET.get('id', '')
    course = Course.objects.get(id = course_id)
    score_range_exist_list = []

    background_set = ["#32C9A6", "#E2BCBE", "#F9D8A7"]
    index = 0
    for course_by_year in course.coursebyyear_set.all().order_by('-course_no'):
        # print (course_by_year.scoredistribution)
        if hasattr(course_by_year, 'scoredistribution'):
            data = {}
            data['course_no'] = course_by_year.course_no
            data['backgroundColor'] = background_set[index]
            data['label'] = course_by_year.course_no[:3] + '學年' + ('上' if course_by_year.course_no[3:5] == '10' else '下')
            data['data'] = [float(x) if x else 0 for x in course_by_year.scoredistribution.score_data[:24:2]]
            data['borderWidth'] = 1
            score_range_exist_list.append(data)
            index += 1
            if index == 3:
                break

    response = JsonResponse(score_range_exist_list, safe=False)
    return response


# private

def replace(string):
    result = re.findall('[\u4e00-\u9fa5]+', string)
    return ', '.join(result)
