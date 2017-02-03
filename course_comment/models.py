# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from course.models import Course

class Comment(models.Model):
    title = models.CharField(max_length = 255)
    content = models.TextField()
    sweety = models.IntegerField(default = 0)     # 甜度
    cold = models.IntegerField(default = 0)       # 涼度
    hardness = models.IntegerField(default = 0)   # 難度
    anonymous = models.BooleanField(default = False)
    course = models.ForeignKey(Course)
    user = models.ForeignKey(User)
    created_time = models.DateTimeField()
    score_img = models.FileField(upload_to = 'docs/', null = True)
