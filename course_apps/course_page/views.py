from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db.models import Q, Avg
from django.views import View
import django_rq
from course_apps.course_page.worker import add_course_func
from course_apps.course_page.models import Course
from mixins.login import LoginRequireMixin


class CoursePageList(LoginRequireMixin, View):
    """
    課程列表
    """
    permission_denied_message = '請先登入呦'

    def get(self, request):
        courses = Course.get_courses()
        paginator = Paginator(courses, 10)  # Show 10 post per page
        page = request.GET.get('page', '')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            results = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results.
            results = paginator.page(paginator.num_pages)

        return render(request, 'course_page/index.html', locals())


class CoursePageDetail(LoginRequireMixin, View):
    """
    課程頁面
    """
    def get(self, request, course_id):
        course = Course.get_course(course_id)
        posts = course.get_posts()
        posts_amount = posts.count()

        sweety_average = posts.aggregate(Avg('sweety'))['sweety__avg'] or 0.0
        cold_average = posts.aggregate(Avg('cold'))['cold__avg'] or 0.0
        hardness_average = (
            posts.aggregate(Avg('hardness'))['hardness__avg'] or 0.0
        )
        sweety_average = round(sweety_average, 1)
        cold_average = round(cold_average, 1)
        hardness_average = round(hardness_average, 1)

        if not request.user.is_anonymous:
            user_score_range = request.user.scoredistribution_set.exists()
            course_score_range = course.coursebyyear_set.filter(
                scoredistribution__isnull=False).exists()
        return render(request, 'course_page/show.html', locals())        


def search(request):
    keyword = request.GET.get('keyword', '')
    all_courses = Course.objects.filter(Q(title_tw__icontains=keyword) | Q(teacher__icontains=keyword) | Q(course_no__icontains=keyword))
    all_courses = all_courses.order_by('course_no')
    paginator = Paginator(all_courses, 10)  # Show 10 post per page

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


def add_course(request):
    print('before')
    queue = django_rq.get_queue('high')
    queue.enqueue(add_course_func)
    print('after')
    return redirect('/')
