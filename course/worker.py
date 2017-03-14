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

def import_course_score_range_func (ACIXSTORE, user):
    
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
            score_range_data_list = score_range_data.replace('\xa0', '').replace(' ','').replace('%', '').split('\n')[2:]
            # print (score_range_data_list[0].decode('utf8'))

            course_data_col = i.find_all('td')
            course_no = course_data_col[0].text + course_data_col[1].text + course_data_col[2].text.replace('\xa0', '')

            course_by_year = CourseByYear.objects.get(course_no = course_no)
            ScoreRange.objects.update_or_create(
                    course = course_by_year,
                    defaults = {
                        "user": user,
                        "course": course_by_year,
                        "score_data": score_range_data_list,
                    } 
                )
            print (course_by_year.course.title_tw)
            print (score_range_data_list)
            # print ('-'*100)
        except  Exception as e:
            print (str(e))
            continue
