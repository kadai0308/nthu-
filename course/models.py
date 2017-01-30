from django.db import models

# Create your models here.
class Course (models.Model):
    course_no = models.CharField(max_length = 255)
    title_tw = models.CharField(max_length = 255)
    title_en = models.CharField(max_length = 255)
    credit = models.CharField(max_length = 255)
    teacher = models.CharField(max_length = 255)
    semester = models.CharField(max_length = 255)
    department = models.CharField(max_length = 255)

class Teacher (models.Model):
    pass

class Deparment (models.Model):
    pass