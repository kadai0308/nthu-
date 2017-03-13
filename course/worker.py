from course.models import Course, CourseByYear, ScoreRange

import os
from functools import wraps
import json
import requests
from bs4 import BeautifulSoup
import html
import django_rq

def add_course_func ():
    years = range(99, 106)
    semesters = [10, 20]

    for year in years:
        for semester in semesters:
            url = 'https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/OPENDATA/open_course_data_{:0>3}{}.json'.format(year, semester)
            all_courses = requests.get(url).text
            all_courses = json.loads(all_courses)
            for course in all_courses:
                dep = course['科號'][5:9].replace(' ','')
                # get_or_create return (object, created)
                print (year, semester,course['課程中文名稱'])
                course_in_db = Course.objects.get_or_create(
                        title_tw = course['課程中文名稱'],
                        teacher = course['授課教師'],
                        defaults = {
                            'title_tw': html.unescape(course['課程中文名稱']),
                            'title_en': course['課程英文名稱'],
                            'credit': course['學分數'],
                            'teacher': html.unescape(course['授課教師']),
                            'department': dep,
                        }
                    )
                course_in_db[0].coursebyyear_set.get_or_create(
                        course_no = course['科號'],
                        defaults = {
                            'course_no': course['科號'],
                            'room_and_time': course['教室與上課時間'],
                        }
                    )