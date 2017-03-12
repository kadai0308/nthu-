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

def score_range (request):
    course_id = request.GET.get('id', '')
    course = Course.objects.get(id = course_id)
    score_range_exist_list = []

    background_set = ["#32C9A6", "#E2BCBE", "#F9D8A7"]
    index = 0
    for course_by_year in course.coursebyyear_set.all().order_by('-course_no'):
        if hasattr(course_by_year, 'scorerange'):
            data = {}
            data['course_no'] = course_by_year.course_no
            data['backgroundColor'] = background_set[index]
            data['label'] = course_by_year.course_no[:3] + '學年' + ('上' if course_by_year.course_no[3:5] == '10' else '下')
            data['data'] = [float(x) if x else 0 for x in course_by_year.scorerange.score_data[:24:2]]
            data['borderWidth'] = 1
            score_range_exist_list.append(data)
            index += 1
            if index == 3:
                break

    response = JsonResponse(score_range_exist_list, safe = False)
    return response

# private

def replace (string):
    
    result = re.findall('[\u4e00-\u9fa5]+', string)
    return ', '.join(result)



# for i in Course.objects.all():
#     i.course_no = i.course_no[5:]
#     i.save()

# for i in Course.objects.all():
#     search = Course.objects.filter(title_tw=i.title_tw, teacher = i.teacher)
#     if len(search) > 1:
#         print (len(search), i.title_tw, i.teacher)


# for i in Course.objects.objects.filter(comment_set__isnull=False):
#     search = Course.objects.filter(course_no=i.course_no)
#     if len(search) > 1:
#         rep = list(set(search) - set(i))
#         if rep.title_tw == i.title_tw:
#             if rep.comment_set and not i.comment_set:
#                 i.delete()
#                 print (1)
#             elif not rep.comment_set and i.comment_set:
#                 rep.delete()
#                 print (2)
#             elif rep.comment_set and i.comment_set:
#                 for comment in rep.comment_set.all():
#                     comment.course = i
#                     comment.save()
#                 rep.save()
#                 print (3)
#             else:
#                 rep.delete()
#                 print (4)

# for i in Course.objects.all():
#     search = Course.objects.filter(title_tw = i.title_tw, teacher = i.teacher)
#     if len(search) > 1:
#         print (search[0].title_tw)
#         clone_data = model_to_dict(search[0])
#         clone_data.pop('id', None)
#         new_course = Course(**clone_data)
#         new_course.save()
#         for old_course in search:
#             # print (old_course.comment_set.all())
#             old_course.comment_set.all().update(course = new_course)
#             old_course.delete()
#         print (Course.objects.filter(title_tw = i.title_tw, teacher = i.teacher).count())
