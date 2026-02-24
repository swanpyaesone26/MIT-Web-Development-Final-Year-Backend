from django.db import models


#teacher db

class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_name = models.CharField(max_length=100)
    subject_id = models.ForeignKey(Subject,on_delete=models.CASCADE)
    year_id =models.ForeignKey(Year,on_delete=models.CASCADE)
    password = models.CharField(max_length=100)
    room_id = models.ForeignKey(Room,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





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




