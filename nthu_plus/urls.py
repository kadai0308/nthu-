"""nthu_plus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.conf.urls.static import static

import api.views as api
from main.views import login, index
from course.views import add_course
import course_comment.views
import users.views

urlpatterns = (
    url(r'^admin/', admin.site.urls),
)

# package setting
urlpatterns += (
    url(r'^accounts/social/login/cancelled/$', users.views.login_cancelled),
    url(r'^accounts/', include('allauth.urls')),
)

# main
urlpatterns += (
    url(r'^$', index),
    # url(r'^login/$', login),
)

# course 
urlpatterns += (
    url(r'^course/add_course$', add_course),
)

# course_comment
urlpatterns += (
    url(r'^course_comment/$', course_comment.views.index),
    url(r'^course_comment/new$', course_comment.views.new),
    url(r'^course_comment/create$', course_comment.views.create),
    url(r'^course_comment/search$', course_comment.views.search),
    url(r'^course_comment/(?P<comment_id>[0-9]+)/edit$', course_comment.views.edit),
    url(r'^course_comment/(?P<comment_id>[0-9]+)/update$', course_comment.views.update),
    url(r'^course_comment/(?P<comment_id>[0-9]+)/delete$', course_comment.views.delete),
)

# user
urlpatterns += (
    url(r'^users/(?P<user_id>[0-9]+)$', users.views.show),
    url(r'^users/(?P<user_id>[0-9]+)/edit$', users.views.edit),
    url(r'^users/(?P<user_id>[0-9]+)/update$', users.views.update),
    url(r'^users/(?P<user_id>[0-9]+)/course_comment$', users.views.course_comment),
)

# api
urlpatterns += (
    url(r'^api/course/search$', api.search_course),
    url(r'^api/comment/search$', api.search_comment),
)