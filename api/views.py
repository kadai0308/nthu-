from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q

from course.models import Course
from course_comment.models import Comment

import re

def search_course (request):
    # dep = request.GET.get('dep','')
    # courses = Course.objects.filter(department = dep)#.extra(select={'sub_course_no': "SUBSTR(course_no, 9)"})
    
    keyword = request.GET.get('keyword', '')
    courses = Course.objects.filter(Q(title_tw__icontains = keyword) | Q(teacher__icontains = keyword) | Q(course_no__icontains = keyword))

    courses = courses.order_by('title_tw', 'teacher')

    data = list()
    for index, course in enumerate(courses):
        # if data and courses[index - 1].title_tw == course.title_tw and courses[index - 1].teacher == course.teacher:
        #     continue

        course_data = dict()
        course_data['title'] = course.title_tw
        course_data['teacher'] = replace(course.teacher)
        course_data['course_no'] = course.course_no
        data.append(course_data)

    # sort by course_no
    data = sorted(data, key = lambda course: course['course_no'][4:])

    response = JsonResponse(data, safe = False)
    return response

def search_comment (request):
    course_no = request.GET['course_no']
    comments = Comment.objects.filter(course__course_no = course_no)

    data = list()

    for comment in comments:
        comment_data = dict()
        comment_data['title'] = comment.course.title_tw
        comment_data['teacher'] = replace(comment.course.teacher)
        comment_data['content'] = comment.content
        comment_data['sweety'] = comment.sweety
        comment_data['cold'] = comment.cold
        comment_data['hardness'] = comment.hardness
        comment_data['user'] = comment.user.profile.nickname
        data.append(comment_data)

    response = JsonResponse(data, safe = False)
    return response

# private

def replace (string):
    
    result = re.findall('[\u4e00-\u9fa5]+', string)
    return ', '.join(result)


