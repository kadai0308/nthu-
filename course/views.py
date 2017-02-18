# -*- coding: utf-8 -*-
from django.shortcuts import render

from course.models import Course

import json
import requests

def index (request):
    pass

def show (request):
    pass

def add_course (request):
    urls = ['https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/OPENDATA/open_course_data.json', 'https://www.ccxp.nthu.edu.tw/ccxp/INQUIRE/JH/OPENDATA/open_course_data_10510.json']
    for url in urls:
        all_courses = requests.get(url).text
        all_courses = json.loads(all_courses)
        for course in all_courses:
            dep = course['科號'][5:9].replace(' ','')
            Course.objects.get_or_create(
                course_no = course['科號'],
                defaults = {
                    'course_no': course['科號'],
                    'title_tw': course['課程中文名稱'],
                    'title_en': course['課程英文名稱'],
                    'credit': course['學分數'],
                    'teacher': course['授課教師'],
                    'department': dep,
                }
            )


def uniq(seq):
    seen = dict()
    dep = seq[::2]
    limit = seq[1::2]
    for index, i in enumerate(dep):
        if not i in seen:
            seen[i] = limit[index]
    return seen