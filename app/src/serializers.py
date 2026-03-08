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
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    is_closed = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'assignment_id', 'assignment_name', 'description',
            'teacher', 'teacher_name',
            'due_date', 'is_closed',
            'created_at', 'updated_at',
        ]
        read_only_fields = ('teacher',)

    def get_is_closed(self, obj):
        if obj.due_date:
            return timezone.now() > obj.due_date
        return False


class StudentAssignmentSerializer(serializers.ModelSerializer):
    """Used by student — includes submission status & score for each assignment."""
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    subject_name = serializers.CharField(source='teacher.subject.subject_name', read_only=True)
    is_closed = serializers.SerializerMethodField()
    submission_status = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    submitted_at = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'assignment_id', 'assignment_name', 'description',
            'teacher_name', 'subject_name',
            'due_date', 'is_closed',
            'submission_status', 'score', 'submitted_at',
            'created_at',
        ]

    def _get_submission(self, obj):
        submission_map = self.context.get('submission_map', {})
        return submission_map.get(obj.assignment_id)

    def get_is_closed(self, obj):
        if obj.due_date:
            return timezone.now() > obj.due_date
        return False

    def get_submission_status(self, obj):
        submission = self._get_submission(obj)
        if submission:
            return 'scored' if submission.score is not None else 'submitted'
        return 'not_submitted'

    def get_score(self, obj):
        submission = self._get_submission(obj)
        return submission.score if submission else None

    def get_submitted_at(self, obj):
        submission = self._get_submission(obj)
        return submission.submitted_at if submission else None


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
