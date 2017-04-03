from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.contrib import messages
from django.db.models import Q
from django.db.models import Avg
from django.http import JsonResponse

from course_apps.course_page.models import Course, CourseByYear, ScoreDistribution
ScoreRange = ScoreDistribution

import course.models as old_course
import course_apps.course_page.models as new_course

import os
from functools import wraps
import json
import requests
from bs4 import BeautifulSoup
import html
import django_rq
from course_apps.course_page.worker import add_course_func, import_course_score_range_func, copy_coursebyyear_data

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

    return render(request, 'course_page/index.html', locals())
    

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

def copy_course_data (request):
    for course in old_course.Course.objects.all():
        new = new_course.Course.objects.create()
        new.title_tw = course.title_tw
        new.title_en = course.title_en
        new.teacher = course.teacher
        new.credit = course.credit
        new.department = course.department
        new.save()

def copy_courseyear_data (request):
    for data in old_course.CourseByYear.objects.all():
        new = new_course.CourseByYear.objects.create()
        new.course_no = data.course_no
        new.room_and_time = data.room_and_time
        course_title = data.course.title_tw
        course_teacher = data.course.teacher
        a = new_course.Course.objects.filter(title_tw = course_title, teacher = course_teacher)
        if a.count() > 1:
            print (a[0].title_tw, a[0].teacher)
        new.course = new_course.Course.objects.get(title_tw = course_title, teacher = course_teacher)
        new.save()

def copy_score_data (request):
    for score in old_course.ScoreRange.objects.all():
        new = new_course.ScoreDistribution.objects.create()
        course = new_course.CourseByYear.objects.get(course_no = score.course.course_no)
        new.course = course
        new.user = score.user
        new.save()

# for course in Course.objects.all():
#     if len(Course.objects.filter(title_tw = course.title_tw, teacher = course.teacher)) > 1:
#         print (1)


# course_list = {('財務個案研究', '蔡子晧\tTSAI, TZU-HAO\n'), ('莊子選讀', '賴昶亘\tLAI, CHANG-XUAN\n'), ('左傳選讀', '賴昶亘\t\n'), ('學術閱讀與討論', '周曉峯\tCHOU, SCHIAO-FENG\n'), ('資訊系統應用', '王崇喆\t\n'), ('英文一', '林群峯\tLIN, CHUN-FENG\n'), ('工程導論', '洪一峯\tHUNG, YI-FENG\n葉安洲\tYEH, AN-CHOU\n蘇安仲\tSU, AN-CHUNG\n張禎元\tCHANG, JEN-YUAN\n'), ('漢學與物質文化', '陳珏\tCHEN JUE\n'), ('專題演講二', '廖文峯\tLIAW, WEN-FENG\n'), ('普通化學一', '廖文峯\tLIAW, WEN-FENG\n'), ('小說選', '陳珏\tCHEN JUE\n'), ('文獻研究與漢學專題', '陳珏\tCHEN JUE\n'), ('電路與電子學二', '邱瀞德\tCHIU, CHING-TE\n'), ('人類學與當代都市', '許瀞文\tCHING-WEN HSU\n'), ('微生物學實驗', '殷献生\tYIN, HSIEN-SHENG\n藍忠昱\tLAN, CHUNG-YU\n高茂傑\tKAO, MOU-CHIEH\n'), ('工程導論', '劉大佼\tLIU, TA-JO\n洪一峯\tHUNG, YI-FENG\n葉安洲\tYEH, AN-CHOU\n張禎元\tCHANG, JEN-YUAN\n'), ('學術英文寫作', '張瀞文\tCHANG, CHING-WEN\n'), ('作業研究與應用', '洪一峯\tHUNG, YI-FENG\n'), ('華人本土心理學', '黃囇莉\tHUANG, LI-LI\n'), ('基礎英文寫作二', '張瀞文\tCHANG, CHING-WEN\n'), ('演說與簡報', '莊媁婷\tCHUANG, WEI-TING\n'), ('英文三--聽講', '莊媁婷\tCHUANG, WEI-TING\n'), ('書報討論', '殷献生\tYIN, HSIEN-SHENG\n'), ('奈米生醫導論', '許志楧\tHSU, CHIH-YING\n'), ('學習心理與文化', '黃囇莉\tHUANG, LI-LI\n'), ('英文二', '莊媁婷\tCHUANG, WEI-TING\n'), ('英文二', '邱瀞萱\tCHIU, CHING-HSUAN\n'), ('中級英文寫作--文章', '張瀞文\tCHANG, CHING-WEN\n'), ('高級韓語一', '韓京惪\tHAN KYUNG DUK\n'), ('初級韓語二', '韓京惪\tHAN KYUNG DUK\n'), ('中級英文寫作-文章', '張瀞文\tCHANG, CHING-WEN\n'), ('質性研究', '黃囇莉\tHUANG, LI-LI\n陳舜文\tCHEN, SHUN-WEN\n'), ('供應鏈管理', '洪一峯\tHUNG, YI-FENG\n'), ('工程數學', '邱瀞德\tCHIU, CHING-TE\n'), ('計量財務金融導論', '蔡子晧\tTSAI, TZU-HAO\n'), ('科技英文寫作', '温富亮\tWEN, FUH-LIANG\n'), ('唐代傳奇文', '陳珏\tCHEN JUE\n'), ('高級韓語會話一', '韓京惪\tHAN KYUNG DUK\n'), ('閱讀與討論一', '周曉峯\tCHOU, SCHIAO-FENG\n'), ('書報討論一', '黃囇莉\tHUANG, LI-LI\n'), ('Web程式設計、技術與應用', '王崇喆\t\n'), ('正向心理與學習專題', '黃囇莉\tHUANG, LI-LI\n'), ('財務管理', '蔡子晧\tTSAI, TZU-HAO\n'), ('結構生物暨蛋白質體學特論二', '殷献生\tYIN, HSIEN-SHENG\n鄭惠春\tCHENG, HUI-CHUN\n'), ('空間與地方', '許瀞文\tCHING-WEN HSU\n'), ('中級韓語二', '韓京惪\tHAN KYUNG DUK\n'), ('高級韓語會話二', '韓京惪\tHAN KYUNG DUK\n'), ('生物力學', '鄭兆珉\tCHENG, CHAO-MIN\n'), ('奈米生醫材料', '鄭兆珉\tCHENG, CHAO-MIN\n'), ('英文三--聽講', '邱瀞萱\tCHIU, CHING-HSUAN\n'), ('英文一', '莊媁婷\tCHUANG, WEI-TING\n'), ('公司理財', '蔡子晧\tTSAI, TZU-HAO\n'), ('晶片應用系統簡介', '邱瀞德\tCHIU, CHING-TE\n'), ('嵌入式擴增實境應用', '邱瀞德\tCHIU, CHING-TE\n'), ('動物生理學', '殷献生\tYIN, HSIEN-SHENG\n張兗君\tCHANG, YEN-CHUNG\n林立元\tLIN, LIH-YUAN\n'), ('結構生物暨蛋白質體學特論二', '殷献生\tYIN, HSIEN-SHENG\n呂平江\tLYU, PING-CHIANG\n'), ('戲曲選', '陳珏\tCHEN JUE\n'), ('書報討論(無機組)', '廖文峯\tLIAW, WEN-FENG\n'), ('英文三--聽講', '張瀞文\tCHANG, CHING-WEN\n'), ('科技英文寫作', '周曉峯\tCHOU, SCHIAO-FENG\n'), ('初級韓語一', '韓京惪\tHAN KYUNG DUK\n'), ('工程導論', '劉大佼\tLIU, TA-JO\n蔡宏營\tTSAI, HUNG-YIN\n洪一峯\tHUNG, YI-FENG\n葉安洲\tYEH, AN-CHOU\n'), ('演說與簡報', '林群峯\tLIN, CHUN-FENG\n'), ('高級財務管理', '蔡子晧\tTSAI, TZU-HAO\n余士迪\tYU, SHIH-TI\n'), ('微奈米科技', '李昇憲\tLI, SHENG-SHIAN\n鄭兆珉\tCHENG, CHAO-MIN\n饒達仁\tYAO, DA-JENG\n'), ('論孟選讀', '賴昶亘\t\n'), ('微生物學實驗', '殷献生\tYIN, HSIEN-SHENG\n高茂傑\tKAO, MOU-CHIEH\n藍忠昱\tLAN, CHUNG-YU\n'), ('醫用病毒學', '殷献生\tYIN, HSIEN-SHENG\n吳夙欽\tWU, SUH-CHIN\n'), ('專題演講', '廖文峯\tLIAW, WEN-FENG\n'), ('計算機程式語言', '洪一峯\tHUNG, YI-FENG\n'), ('英文三--閱讀', '林群峯\tLIN, CHUN-FENG\n'), ('長壽風險管理', '蔡子晧\tTSAI, TZU-HAO\n'), ('英文二', '張瀞文\tCHANG, CHING-WEN\n'), ('書報討論', '蔡子晧\tTSAI, TZU-HAO\n'), ('都市人類學', '許瀞文\tCHING-WEN HSU\n'), ('工程導論', '劉大佼\tLIU, TA-JO\n張禎元\tCHANG, JEN-YUAN\n洪一峯\tHUNG, YI-FENG\n葉安洲\tYEH, AN-CHOU\n'), ('基因晶片及其生醫應用', '許志楧\tHSU, CHIH-YING\n'), ('人類學研究方法', '許瀞文\tCHING-WEN HSU\n'), ('書報討論', '鄭兆珉\tCHENG, CHAO-MIN\n'), ('東方思想經典：《莊子》選讀', '賴昶亘\tLAI, CHANG-XUAN\n'), ('免疫學', '殷献生\tYIN, HSIEN-SHENG\n張鑑中\tCHANG, CHIEN-CHUNG\n'), ('中級英語聽講二', '邱瀞萱\tCHIU, CHING-HSUAN\n'), ('莊子選讀', '賴昶亘\t\n'), ('工程創意思維專題', '劉大佼\tLIU, TA-JO\n洪一峯\tHUNG, YI-FENG\n葉安洲\tYEH, AN-CHOU\n張禎元\tCHANG, JEN-YUAN\n曾正宜\tTZENG, JENG-YI\n李紫原\tLEE, CHI-YOUNG\n'), ('中級韓語一', '韓京惪\tHAN KYUNG DUK\n'), ('衍生性商品與程式交易', '蔡子晧\tTSAI, TZU-HAO\n'), ('文化人類學專題', '許瀞文\tCHING-WEN HSU\n'), ('保健物理', '蘇献章\tSU, SHIAN-JANG\n'), ('進修英文', '張瀞文\tCHANG, CHING-WEN\n'), ('微系統於重點照護檢驗之應用', '鄭兆珉\tCHENG, CHAO-MIN\n'), ('大學中文', '張莅\t\n'), ('程式設計入門', '王崇喆\t\n'), ('工程導論', '劉大佼\tLIU, TA-JO\n葉安洲\tYEH, AN-CHOU\n洪一峯\tHUNG, YI-FENG\n張禎元\tCHANG, JEN-YUAN\n'), ('生醫工程與環境科學導論', '黃郁棻\tHUANG, YU-FEN\n許志楧\tHSU, CHIH-YING\n周文采\tCHOU, WEN-TSAE\n'), ('微生物學', '殷献生\tYIN, HSIEN-SHENG\n藍忠昱\tLAN, CHUNG-YU\n高茂傑\tKAO, MOU-CHIEH\n'), ('生物無機化學', '廖文峯\tLIAW, WEN-FENG\n'), ('商用會話', '莊媁婷\tCHUANG, WEI-TING\n'), ('大學中文', '賴昶亘\tLAI, CHANG-XUAN\n'), ('進階學術英文', '張瀞文\tCHANG, CHING-WEN\n'), ('英文一', '張瀞文\tCHANG, CHING-WEN\n')}
# for data in course_list:
#     courses = Course.objects.filter(title_tw=data[0], teacher = data[1])
#     order = 1
#     for course in courses:
#             if course.coursebyyear_set.exists():
#                     print (order)
#                     order+=1

# for data in course_list:
#     courses = Course.objects.filter(title_tw=data[0], teacher = data[1])
#     for course in courses:
#         for year in course.coursebyyear_set.all():
#             year.course = courses[0]
#             year.save()

# delete_id = []        
# for data in course_list:
#     courses = Course.objects.filter(title_tw=data[0], teacher = data[1])
#     for course in courses:
#         if not course.coursebyyear_set.exists() and not course.comment_set.exists():
#             delete_id.append(course.id)

# for id in delete_id:
#     course = Course.objects.get(id = id).delete()
#     if course.coursebyyear_set.exists():
#         print (1)
#     elif course.comment_set.exists():
#         print (2)
