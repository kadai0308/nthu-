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

from index.views import index, privacy_policy
import course_apps.course_page.views as course_page
import course_apps.course_post.views as course_post
import api.views as api
import users.views as users

urlpatterns = (
    url(r'^admin/', admin.site.urls),
)

# package setting
urlpatterns += (
    url(r'^accounts/', include('allauth.urls')),
)

# main
urlpatterns += (
    url(r'^$', index),
    url(r'^privacypolicy$', privacy_policy),
)

# course 
# urlpatterns += (
#     url(r'^course/$', course.index),
#     url(r'^course/(?P<course_id>[0-9]+)$', course.show),
#     url(r'^course/search$', course.search),
#     url(r'^course/add_course$', course.add_course),
#     url(r'^course/import_course_score_range$', course.import_course_score_range),
# )

# course_page

urlpatterns += (
    url(r'^course_page/$', course_page.index),
    url(r'^course_page/(?P<course_id>[0-9]+)$', course_page.show),
    url(r'^course_page/search$', course_page.search),
    url(r'^course_page/add_course$', course_page.add_course),
    url(r'^course_page/import_course_score_range$', course_page.import_course_score_range),
    url(r'^copy_score_data/$', course_page.copy_score_data),
)

# urlpatterns += (
#     url(r'^test/course/$', course_page.index),
#     url(r'^copy_course_data/$', course_page.copy_course_data),
#     url(r'^copy_courseyear_data/$', course_page.copy_courseyear_data),
#     url(r'^copy_score_data/$', course_page.copy_score_data)
# )


# course_post
# urlpatterns += (
#     url(r'^course_post/$', course_post.index),
#     url(r'^course_post/new$', course_post.new),
#     url(r'^course_post/create$', course_post.create),
#     url(r'^course_post/search$', course_post.search),
#     url(r'^course_post/(?P<post_id>[0-9]+)$', course_post.show),
#     url(r'^course_post/(?P<post_id>[0-9]+)/edit$', course_post.edit),
#     url(r'^course_post/(?P<post_id>[0-9]+)/update$', course_post.update),
#     url(r'^course_post/(?P<post_id>[0-9]+)/delete$', course_post.delete),
# )

# course_post
urlpatterns += (
    url(r'^course_post/$', course_post.index),
    url(r'^course_post/new$', course_post.new),
    url(r'^course_post/create$', course_post.create),
    url(r'^course_post/search$', course_post.search),
    url(r'^course_post/(?P<post_id>[0-9]+)$', course_post.show),
    url(r'^course_post/(?P<post_id>[0-9]+)/edit$', course_post.edit),
    url(r'^course_post/(?P<post_id>[0-9]+)/update$', course_post.update),
    url(r'^course_post/(?P<post_id>[0-9]+)/delete$', course_post.delete),
    url(r'^copy_post_data/$', course_post.copy_post_data),
)

# user
urlpatterns += (
    url(r'^accounts/social/login/cancelled/$', users.login_cancelled),
    url(r'^users/(?P<user_id>[0-9]+)$', users.show),
    url(r'^users/(?P<user_id>[0-9]+)/edit$', users.edit),
    url(r'^users/(?P<user_id>[0-9]+)/update$', users.update),
    url(r'^users/(?P<user_id>[0-9]+)/course_post$', users.course_post),
)

# api
urlpatterns += (
    url(r'^api/course/search$', api.search_course),
    url(r'^api/course/score_range$', api.score_range),
    url(r'^api/post/search$', api.search_post),
)

# rq
urlpatterns += (
    url(r'^django-rq/', include('django_rq.urls')),
)