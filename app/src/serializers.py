from rest_framework import serializers
from django.utils import timezone
from app.src.models import Student, Teacher, Assignment, Submission, Year, Room, Subject

# teacher serializer
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

# student serializer    
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

# year serializer
class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = '__all__'

# room serializer
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

# subject serializer
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


# ───────────── Assignment Serializers ─────────────

class AssignmentSerializer(serializers.ModelSerializer):
    """Used by teacher for CRUD operations."""
    id = serializers.IntegerField(source='assignment_id', read_only=True)
    title = serializers.CharField(source='assignment_name')
    dueDate = serializers.DateTimeField(source='due_date', required=False, allow_null=True)
    subject = serializers.CharField(source='teacher.subject.subject_name', read_only=True)
    submissions = serializers.SerializerMethodField()
    totalStudents = serializers.SerializerMethodField()
    is_closed = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description',
            'dueDate', 'subject',
            'submissions', 'totalStudents',
            'is_closed', 'status',
            'createdAt', 'updatedAt',
        ]

    def get_submissions(self, obj):
        return Submission.objects.filter(assignment=obj).count()

    def get_totalStudents(self, obj):
        rooms = Room.objects.filter(teacher=obj.teacher)
        return Student.objects.filter(rooms__in=rooms).distinct().count()

    def get_is_closed(self, obj):
        if obj.due_date:
            return timezone.now() > obj.due_date
        return False

    def get_status(self, obj):
        if obj.due_date and timezone.now() > obj.due_date:
            return "overdue"
        return "active"


class StudentAssignmentSerializer(serializers.ModelSerializer):
    """Used by student — includes submission info for each assignment."""
    id = serializers.IntegerField(source='assignment_id', read_only=True)
    title = serializers.CharField(source='assignment_name', read_only=True)
    dueDate = serializers.DateTimeField(source='due_date', read_only=True)
    subject = serializers.CharField(source='teacher.subject.subject_name', read_only=True)
    score = serializers.SerializerMethodField()
    submitted = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description',
            'dueDate', 'subject',
            'score', 'submitted', 'files',
            'status',
        ]

    def _get_submission(self, obj):
        submission_map = self.context.get('submission_map', {})
        return submission_map.get(obj.assignment_id)

    def get_score(self, obj):
        submission = self._get_submission(obj)
        return submission.score if submission else None

    def get_submitted(self, obj):
        return self._get_submission(obj) is not None

    def get_files(self, obj):
        submission = self._get_submission(obj)
        if submission and submission.file:
            return submission.file.url
        return ""

    def get_status(self, obj):
        if obj.due_date and timezone.now() > obj.due_date:
            return "overdue"
        return "active"


# ───────────── Submission Serializers ─────────────

class SubmissionSerializer(serializers.ModelSerializer):
    """Used for teacher viewing submissions and student submitting."""
    student_name = serializers.CharField(source='student.student_name', read_only=True)
    assignment_name = serializers.CharField(source='assignment.assignment_name', read_only=True)

    class Meta:
        model = Submission
        fields = [
            'submission_id', 'assignment', 'assignment_name',
            'student', 'student_name',
            'file', 'score',
            'submitted_at', 'updated_at',
        ]
        read_only_fields = ('student', 'assignment', 'submitted_at', 'score')


class StudentScoreSerializer(serializers.ModelSerializer):
    """Used by student to view their scores with assignment details."""
    assignment_name = serializers.CharField(source='assignment.assignment_name', read_only=True)
    teacher_name = serializers.CharField(source='assignment.teacher.teacher_name', read_only=True)
    subject_name = serializers.CharField(source='assignment.teacher.subject.subject_name', read_only=True)

    class Meta:
        model = Submission
        fields = [
            'submission_id', 'assignment_name',
            'teacher_name', 'subject_name',
            'file', 'score',
            'submitted_at',
        ]
