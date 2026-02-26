from django.contrib import admin
from .models import Teacher, Student, Year, Subject, Room
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin

# Unregister the default User and Group models from the admin site to avoid confusion, since we are not using them in our app. Just using Unfold
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

# need to register, maybe we do next this and other user models
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'teacher_name', 'subject', 'year', 'created_at', 'updated_at')
    search_fields = ('teacher_name','subject','year')
    ordering = ('year',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'student_name', 'year', 'created_at', 'updated_at')
    search_fields = ('student_name','year')
    ordering = ('year',)

@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ('year_id', 'year_name', 'created_at', 'updated_at')
    search_fields = ('year_name',)
    ordering = ('year_name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_id', 'subject_name', 'created_at', 'updated_at')
    search_fields = ('subject_name',)
    ordering = ('subject_name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'room_name', 'created_at', 'updated_at')
    search_fields = ('room_name',)
    ordering = ('year',)


