from rest_framework import serializers
from app.src.models import Student, Teacher, Assignment, Year, Room, Subject

# teacher serializer
class TeacherSerializer(serializers.Serializer):
    class Meta:
        model = Teacher
        fields = '__all__'

# student serializer    
class StudentSerializer(serializers.Serializer):
    class Meta:
        model = Student
        fields = '__all__'

# assignment serializer
class AssignmentSerializer(serializers.Serializer):
    class Meta:
        model = Assignment
        fields = '__all__'

# year serializer
class YearSerializer(serializers.Serializer):
    class Meta:
        model = Year
        fields = '__all__'

# room serializer
class RoomSerializer(serializers.Serializer):
    class Meta:
        model = Room
        fields = '__all__'

# subject serializer
class SubjectSerializer(serializers.Serializer):
    class Meta:
        model = Subject
        fields = '__all__'
