from django.db import models

#teacher db
class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_name = models.CharField(max_length=100)
    subject = models.OneToOneField('Subject', on_delete=models.CASCADE)
    year = models.OneToOneField('Year', on_delete=models.CASCADE)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.teacher_name
    
    class Meta:
        db_table = 'teacher'

# student db
class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=100)
    rooms = models.ManyToManyField('Room')
    year = models.OneToOneField('Year', on_delete=models.CASCADE)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_name

    class Meta:
        db_table = 'student'

#assignment db
class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    assignment_name = models.CharField(max_length=250)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    rooms = models.ManyToManyField('Room')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.assignment_name

    class Meta:
        db_table = 'assignment'

#year db
class Year(models.Model):
    year_id = models.AutoField(primary_key=True)
    year_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.year_name

    class Meta:
        db_table = 'year'

#room db
class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    room_name = models.CharField(max_length=100, unique=True)
    teacher = models.OneToOneField('Teacher', on_delete=models.CASCADE)
    subject = models.OneToOneField('Subject', on_delete=models.CASCADE)
    year = models.OneToOneField('Year', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.room_name

    class Meta:
        db_table = 'room'

#subject db
class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject_name
    
    class Meta:
        db_table = 'subject'
