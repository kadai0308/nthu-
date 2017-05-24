from django.db import models
from jsonfield import JSONField
from datetime import datetime
from django.contrib.auth.models import User


class Course (models.Model):
    course_no = models.CharField(max_length=255)
    title_tw = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    credit = models.CharField(max_length=255)
    teacher = models.TextField()
    semester = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    latest_open_time = models.CharField(max_length=255)


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
