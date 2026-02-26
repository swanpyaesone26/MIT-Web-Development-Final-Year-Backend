from django.contrib import admin
from .models import Teacher, Student, Year, Subject, Room
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin

# Unregister the default User and Group models from the admin site to avoid confusion, since we are not using them in our app. Just using Unfold
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(Teacher, ModelAdmin)
admin.site.register(Student, ModelAdmin)
admin.site.register(Year, ModelAdmin)
admin.site.register(Subject, ModelAdmin)
admin.site.register(Room, ModelAdmin)   