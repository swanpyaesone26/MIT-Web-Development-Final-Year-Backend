from django.db import models


#teacher db

class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_name = models.CharField(max_length=100)
    subject_id = models.ForeignKey(Subject,on_delete=models.CASCADE)





# student db
class Student(models.Model):






#assignment db
class Assignment(models.Model):




#year db
class Year(models.Model):


#room db
class Room(models.Model):



#subject db
class Subject(models.Model):




