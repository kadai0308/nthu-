from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, render_to_response
from django.contrib import messages
from functools import wraps
from django.db.models import Q
from django.views import View
from course_apps.course_page.models import Course
from course_apps.course_post.models import Post

import datetime
from mixins.login import OwnerCheckMixin

# private
def _check_post_auth(view):
    @wraps(view)
    def check(request, *args, **kargs):
        if not request.user.is_authenticated():
            messages.warning(request, '請先登入呦')
            return redirect ('/')

        if 'post_id' in kargs:
            post = Post.objects.get(id = kargs['post_id'])
            if post.user.id != request.user.id:
                messages.warning(request, '權限不符')
                return redirect('/')

            return view(request, post)

        return view(request)

    return check


# @_check_post_auth
def index (request):
    if not request.user.post_set.exists():
        ban = False #time for new student comming
        # ban = 'ban'

    all_posts = Post.objects.all().order_by('-created_time')
    course_post = 'focus'

    paginator = Paginator(all_posts, 10) # Show 10 conmment per page

    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    return render(request, 'course_post/index.html', locals())

@_check_post_auth
def new (request):
    course_id = request.GET.get('course_id', '')
    if course_id:
        course = Course.objects.get(id = int(course_id))

    return render(request, 'course_post/new.html', locals())

@_check_post_auth
def create (request):
    
    # get course
    course_id = request.POST.get('course_no', '')

    # if course_id == '':
    #     return redirect(request.META.get('HTTP_REFERER'))

    title = request.POST.get('title', '')
    teacher = request.POST.get('teacher', '')
    scoring = request.POST.get('scoring', '')
    content = request.POST.get('content', '')

    total_content = '【評分方式】' + scoring + '\n\n'
    total_content += '【修課心得】' + content + '\n\n'
    
    score_img = request.FILES['score_img'] if 'score_img' in request.FILES else None

    sweety = request.POST['sweety'] if 'sweety' in request.POST else 0
    cold = request.POST['cold'] if 'cold' in request.POST else 0
    hardness = request.POST['hardness'] if 'hardness' in request.POST else 0

    try:
        if course_id:
            course = Course.objects.get(id = course_id)
            # create post of course
            Post.objects.create(
                title = title,
                content = total_content,
                anonymous = True,
                course = course,
                user = request.user,
                created_time = str(datetime.datetime.now()),
                sweety = sweety,
                cold = cold,
                hardness = hardness,
                score_img = score_img,
            )
    except  Exception as e: 
        print ('log1:', str(e))
        import sys
        print ('log2:', str(sys.exc_info()))

    return redirect ('/course_post')

def show (request, post_id):
    all_posts = [Post.objects.get(id = post_id)]
    course_post = 'focus'
    paginator = Paginator(all_posts, 10) # Show 10 conmment per page

    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)
    return render(request, 'course_post/index.html', locals())

@_check_post_auth
def edit (request, post):
    return render(request, 'course_post/edit.html', locals())

@_check_post_auth
def update(request, post):

    post.title = request.POST.get('title','')
    post.content = request.POST.get('content','')

    # score_img = request.FILES['score_img'] if 'score_img' in request.FILES else None

    post.sweety = request.POST.get('sweety', 0)
    post.cold = request.POST.get('cold', 0)
    post.hardness = request.POST.get('hardness', 0)

    post.save()

    return redirect('/users/{}/course_post'.format(request.user.id))

@_check_post_auth
def delete(request, post):

    post.delete()

    return redirect('/users/{}/course_post'.format(request.user.id))

def search (request):
    if not request.user.post_set.exists():
        ban = 'ban'
    
    keyword = request.GET.get('keyword', '')
    courses = Course.objects.filter(Q(title_tw__icontains = keyword) | Q(teacher__icontains = keyword) | Q(course_no__icontains = keyword))
    all_posts = Post.objects.filter(course__in = courses).order_by('-created_time')

    if not all_posts:
        no_post = True

    paginator = Paginator(all_posts, 10) # Show 10 contacts per page

    page = request.GET.get('page', 1)
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    # return render(request, 'course_post/index.html', {'contacts': contacts})
    return render(request, 'course_post/index.html', locals())


def copy_post_data (request):
    for comment in Comment.objects.all():
        course = Course.objects.get(title_tw = comment.course.title_tw, teacher = comment.course.teacher)
        new = Post.objects.create(
                title = comment.title,
                custom_course_name = comment.custom_course_name,
                content = comment.content,
                sweety = comment.sweety,
                cold = comment.cold,
                hardness = comment.hardness,
                anonymous = comment.anonymous,
                course = course,
                user = comment.user,
                created_time = str(comment.created_time)        
            )


class CoursePostList(View):

    def get(self, request):
        pass


class CoursePostDetail(OwnerCheckMixin, View):

    permission_denied_message = '權限不符'
    model = Post

    # show
    def get(self, request, post_id):
        all_posts = [Post.objects.get(id=post_id)]
        course_post = 'focus'
        paginator = Paginator(all_posts, 10)  # Show 10 conmment per page

        page = request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            results = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            results = paginator.page(paginator.num_pages)
        return render(request, 'course_post/index.html', locals())

    def put(self, request):
        return render(request, 'course_post/edit.html', locals())

    def delete(self, request):
        pass

