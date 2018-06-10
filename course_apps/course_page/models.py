from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User
from django.db.models import Q


class Course (models.Model):
    course_no = models.CharField(max_length=255)
    title_tw = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    credit = models.CharField(max_length=255)
    teacher = models.TextField()
    semester = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    latest_open_time = models.CharField(max_length=255)

    def __str__(self):
        return self.title_tw

    @staticmethod
    def get_courses():
        # 去除無效課程
        courses = Course.objects.filter(~Q(latest_open_time='暫無資料'))
        # 按照開課時間排
        # 之後可以選擇用什麼排
        courses = courses.order_by('-latest_open_time')
        return courses

    @staticmethod
    def get_course(course_id):
        return Course.objects.get(id=course_id)

    def get_posts(self):
        return self.post_set.all()


class CourseByYear (models.Model):
    course_no = models.CharField(max_length=255)
    room_and_time = models.CharField(max_length=255)
    course = models.ForeignKey(Course, null=True)


class ScoreDistribution (models.Model):
    course = models.OneToOneField(CourseByYear, null=True)
    user = models.ForeignKey(User, null=True)
    semester = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    score_data = JSONField()


class Teacher (models.Model):
    pass


class Deparment (models.Model):
    pass
