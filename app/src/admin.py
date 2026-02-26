from django.contrib import admin
from .models import Teacher, Student, Year, Subject, Room
from unfold.admin import ModelAdmin

admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Year)
admin.site.register(Subject)
admin.site.register(Room)   