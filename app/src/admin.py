from django.contrib import admin
from django import forms
from .models import Teacher, Student, Year, Subject, Room
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password

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


# ───────── Teacher Admin ─────────

class TeacherForm(forms.ModelForm):
    username = forms.CharField(max_length=150, help_text="Login username for this teacher.")
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text="Leave blank to keep existing password (when editing).",
    )

    class Meta:
        model = Teacher
        fields = ('teacher_name', 'subject', 'year')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
        elif not self.instance.pk:
            # New teacher — password is required
            self.fields['password'].required = True

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk and self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def save(self, commit=True):
        teacher = super().save(commit=False)
        username = self.cleaned_data['username']
        password = self.cleaned_data.get('password')

        if teacher.pk and teacher.user:
            # Editing existing teacher
            user = teacher.user
            user.username = username
            if password:
                user.set_password(password)
            user.save()
        else:
            # Creating new teacher
            user = User.objects.create_user(username=username, password=password)
            teacher.user = user

        if commit:
            teacher.save()
            self.save_m2m()
        return teacher


@admin.register(Teacher)
class TeacherAdmin(ModelAdmin):
    form = TeacherForm
    list_display = ('teacher_id', 'teacher_name', 'get_username', 'subject', 'year', 'created_at')
    search_fields = ('teacher_name', 'user__username', 'subject__subject_name', 'year__year_name')
    ordering = ('year',)

    def get_username(self, obj):
        return obj.user.username if obj.user else '—'
    get_username.short_description = 'Username'


# ───────── Student Admin ─────────

class StudentForm(forms.ModelForm):
    username = forms.CharField(max_length=150, help_text="Login username for this student.")
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text="Leave blank to keep existing password (when editing).",
    )

    class Meta:
        model = Student
        fields = ('student_name', 'rooms', 'year')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
        elif not self.instance.pk:
            self.fields['password'].required = True

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk and self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def save(self, commit=True):
        student = super().save(commit=False)
        username = self.cleaned_data['username']
        password = self.cleaned_data.get('password')

        if student.pk and student.user:
            user = student.user
            user.username = username
            if password:
                user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(username=username, password=password)
            student.user = user

        if commit:
            student.save()
            self.save_m2m()
        return student


@admin.register(Student)
class StudentAdmin(ModelAdmin):
    form = StudentForm
    list_display = ('student_id', 'student_name', 'get_username', 'year', 'created_at')
    search_fields = ('student_name', 'user__username', 'year__year_name')
    ordering = ('year',)

    def get_username(self, obj):
        return obj.user.username if obj.user else '—'
    get_username.short_description = 'Username'

@admin.register(Year)
class YearAdmin(ModelAdmin):
    list_display = ('year_id', 'year_name', 'created_at', 'updated_at')
    search_fields = ('year_name',)
    ordering = ('year_name',)

@admin.register(Subject)
class SubjectAdmin(ModelAdmin):
    list_display = ('subject_id', 'subject_name', 'created_at', 'updated_at')
    search_fields = ('subject_name',)
    ordering = ('subject_name',)

@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = ('room_id', 'room_name', 'teacher', 'subject', 'year', 'created_at', 'updated_at')
    search_fields = ('room_name', 'teacher__teacher_name', 'subject__subject_name', 'year__year_name')
    ordering = ('year',)


