from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Avg, F

from app.src.models import Assignment, Submission, Teacher, Student, Room
from app.src.serializers import (
    AssignmentSerializer,
    StudentAssignmentSerializer,
    SubmissionSerializer,
    StudentScoreSerializer,
)


# ───────────── Response helpers ─────────────

def success_response(data=None, message="", status_code=status.HTTP_200_OK):
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return Response(response, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, errors=None):
    response = {"status": "error", "message": message}
    if errors is not None:
        response["errors"] = errors
    return Response(response, status=status_code)


# ───────────────── Auth Views ─────────────────

class CustomLoginView(APIView):
    """Custom login view that wraps JWT tokens with user info."""

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return error_response("Invalid credentials.", status.HTTP_401_UNAUTHORIZED)

        user = serializer.user
        tokens = serializer.validated_data

        role = 'unknown'
        name = user.username
        try:
            role = 'teacher'
            name = user.teacher.teacher_name
        except Teacher.DoesNotExist:
            try:
                role = 'student'
                name = user.student.student_name
            except Student.DoesNotExist:
                pass

        return success_response(
            data={
                'user': {'id': user.id, 'name': name, 'role': role},
                'tokens': {
                    'accessToken': str(tokens['access']),
                    'refreshToken': str(tokens['refresh']),
                },
            },
            message="Login successful",
        )


class CustomTokenRefreshView(APIView):
    """Custom refresh view that accepts refreshToken and returns accessToken."""

    def post(self, request):
        refresh_token = request.data.get('refreshToken') or request.data.get('refresh')
        if not refresh_token:
            return error_response("Refresh token is required.")
        try:
            token = RefreshToken(refresh_token)
            return success_response(
                data={'accessToken': str(token.access_token)},
                message="Access token refreshed successfully",
            )
        except Exception:
            return error_response("Invalid or expired refresh token.", status.HTTP_401_UNAUTHORIZED)


# ───────────────── Teacher Views ─────────────────

class TeacherAssignmentView(APIView):
    """List & create assignments for the authenticated teacher."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return error_response("You are not a teacher.", status.HTTP_403_FORBIDDEN)

        assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')
        serializer = AssignmentSerializer(assignments, many=True, context={'request': request})
        return success_response(data=serializer.data, message="Assignments fetched successfully.")

    def post(self, request):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return error_response("You are not a teacher.", status.HTTP_403_FORBIDDEN)

        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=teacher)
            return success_response(
                data=serializer.data,
                message="Assignment created successfully.",
                status_code=status.HTTP_201_CREATED,
            )
        return error_response("Validation failed.", status.HTTP_400_BAD_REQUEST, errors=serializer.errors)


class TeacherAssignmentDetailView(APIView):
    """Retrieve, update, or delete a single assignment."""
    permission_classes = [IsAuthenticated]

    def _get_assignment(self, request, assignment_id):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return None, error_response("You are not a teacher.", status.HTTP_403_FORBIDDEN)
        try:
            assignment = Assignment.objects.get(assignment_id=assignment_id, teacher=teacher)
        except Assignment.DoesNotExist:
            return None, error_response("Assignment not found.", status.HTTP_404_NOT_FOUND)
        return assignment, None

    def get(self, request, assignment_id):
        assignment, err = self._get_assignment(request, assignment_id)
        if err:
            return err
        serializer = AssignmentSerializer(assignment, context={'request': request})
        return success_response(data=serializer.data, message="Assignment fetched successfully.")

    def put(self, request, assignment_id):
        assignment, err = self._get_assignment(request, assignment_id)
        if err:
            return err
        serializer = AssignmentSerializer(assignment, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, message="Assignment updated successfully.")
        return error_response("Validation failed.", status.HTTP_400_BAD_REQUEST, errors=serializer.errors)

    def delete(self, request, assignment_id):
        assignment, err = self._get_assignment(request, assignment_id)
        if err:
            return err
        assignment.delete()
        return success_response(message="Assignment deleted successfully.")


class TeacherAssignmentCloseView(APIView):
    """Close an assignment early (sets due_date to now)."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, assignment_id):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return error_response("You are not a teacher.", status.HTTP_403_FORBIDDEN)
        try:
            assignment = Assignment.objects.get(assignment_id=assignment_id, teacher=teacher)
        except Assignment.DoesNotExist:
            return error_response("Assignment not found.", status.HTTP_404_NOT_FOUND)

        assignment.due_date = timezone.now()
        assignment.save()
        serializer = AssignmentSerializer(assignment, context={'request': request})
        return success_response(data=serializer.data, message="Assignment closed successfully.")


class TeacherSubmissionListView(APIView):
    """Teacher views all submissions for a specific assignment."""
    permission_classes = [IsAuthenticated]

    def get(self, request, assignment_id):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return error_response("You are not a teacher.", status.HTTP_403_FORBIDDEN)
        try:
            assignment = Assignment.objects.get(assignment_id=assignment_id, teacher=teacher)
        except Assignment.DoesNotExist:
            return error_response("Assignment not found.", status.HTTP_404_NOT_FOUND)

        submissions = Submission.objects.filter(assignment=assignment).select_related('student', 'assignment')
        serializer = SubmissionSerializer(submissions, many=True, context={'request': request})
        return success_response(data=serializer.data, message="Submissions fetched successfully.")


class TeacherScoreView(APIView):
    """Teacher gives score to a submission."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, submission_id):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return error_response("You are not a teacher.", status.HTTP_403_FORBIDDEN)

        try:
            submission = Submission.objects.select_related('student').get(
                submission_id=submission_id,
                assignment__teacher=teacher,
            )
        except Submission.DoesNotExist:
            return error_response("Submission not found.", status.HTTP_404_NOT_FOUND)

        score = request.data.get('score')
        if score is None:
            return error_response("Score is required.")

        submission.score = score
        submission.save()
        file_url = None
        if submission.file:
            file_url = request.build_absolute_uri(submission.file.url)
        data = {
            'studentId': submission.student.student_id,
            'name': submission.student.student_name,
            'score': submission.score,
            'submitted': True,
            'file': file_url,
        }
        return success_response(data=data, message="Score updated successfully.")


# ───────────────── Student Views ─────────────────

class StudentAssignmentView(APIView):
    """Student views all assignments from their rooms (assignment dashboard)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return error_response("You are not a student.", status.HTTP_403_FORBIDDEN)

        student_rooms = student.rooms.all()
        teachers = Teacher.objects.filter(room__in=student_rooms)
        assignments = (
            Assignment.objects
            .filter(teacher__in=teachers)
            .select_related('teacher', 'teacher__subject')
            .order_by('-created_at')
        )

        # Build submission map to avoid N+1 queries
        submissions = Submission.objects.filter(student=student, assignment__in=assignments)
        submission_map = {s.assignment_id: s for s in submissions}

        serializer = StudentAssignmentSerializer(
            assignments, many=True,
            context={'request': request, 'student': student, 'submission_map': submission_map},
        )
        return success_response(data=serializer.data, message="Assignments fetched successfully.")


class StudentSubmitView(APIView):
    """Student submits a file for an assignment (blocked after due date)."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, assignment_id):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return error_response("You are not a student.", status.HTTP_403_FORBIDDEN)

        student_rooms = student.rooms.all()
        teachers = Teacher.objects.filter(room__in=student_rooms)
        try:
            assignment = Assignment.objects.get(assignment_id=assignment_id, teacher__in=teachers)
        except Assignment.DoesNotExist:
            return error_response("Assignment not found.", status.HTTP_404_NOT_FOUND)

        # Due-date check — block submission after deadline (like Google Classroom)
        if assignment.due_date and timezone.now() > assignment.due_date:
            return error_response(
                "Assignment is closed. The due date has passed.",
                status.HTTP_403_FORBIDDEN,
            )

        if Submission.objects.filter(assignment=assignment, student=student).exists():
            return error_response("You have already submitted this assignment.")

        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            submission = serializer.save(assignment=assignment, student=student)
            file_url = None
            if submission.file:
                file_url = request.build_absolute_uri(submission.file.url)
            data = {
                'assignmentId': assignment.assignment_id,
                'studentId': student.student_id,
                'submitted': True,
                'file': file_url,
                'score': None,
                'submittedAt': submission.submitted_at,
            }
            return success_response(
                data=data,
                message="Assignment submitted successfully.",
                status_code=status.HTTP_201_CREATED,
            )
        return error_response("Validation failed.", status.HTTP_400_BAD_REQUEST, errors=serializer.errors)


class StudentScoreView(APIView):
    """Student views their scores for all submitted assignments."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return error_response("You are not a student.", status.HTTP_403_FORBIDDEN)

        submissions = Submission.objects.filter(student=student).select_related(
            'assignment', 'assignment__teacher', 'assignment__teacher__subject',
        )
        serializer = StudentScoreSerializer(submissions, many=True, context={'request': request})
        return success_response(data=serializer.data, message="Scores fetched successfully.")


class StudentBarChartView(APIView):
    """Returns average scores grouped by subject for bar chart display."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return error_response("You are not a student.", status.HTTP_403_FORBIDDEN)

        scores = list(
            Submission.objects
            .filter(student=student, score__isnull=False)
            .values(subject=F('assignment__teacher__subject__subject_name'))
            .annotate(score=Avg('score'))
            .order_by('subject')
        )
        return success_response(data=scores, message="Scores fetched successfully.")


# ───────────────── Profile View ─────────────────

class UserProfileView(APIView):
    """Returns user type and profile information after login."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Check if user is a teacher
        try:
            teacher = user.teacher
            rooms = Room.objects.filter(teacher=teacher)
            return success_response(
                data={
                    'user_type': 'teacher',
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'profile': {
                        'teacher_id': teacher.teacher_id,
                        'teacher_name': teacher.teacher_name,
                        'subject': {
                            'subject_id': teacher.subject.subject_id,
                            'subject_name': teacher.subject.subject_name,
                        },
                        'year': {
                            'year_id': teacher.year.year_id,
                            'year_name': teacher.year.year_name,
                        },
                        'rooms': [{'room_id': r.room_id, 'room_name': r.room_name} for r in rooms],
                    },
                },
                message="Profile fetched successfully.",
            )
        except Teacher.DoesNotExist:
            pass

        # Check if user is a student
        try:
            student = user.student
            student_rooms = student.rooms.all()
            return success_response(
                data={
                    'user_type': 'student',
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'profile': {
                        'student_id': student.student_id,
                        'student_name': student.student_name,
                        'year': {
                            'year_id': student.year.year_id,
                            'year_name': student.year.year_name,
                        },
                        'rooms': [{'room_id': r.room_id, 'room_name': r.room_name} for r in student_rooms],
                    },
                },
                message="Profile fetched successfully.",
            )
        except Student.DoesNotExist:
            pass

        return error_response(
            "User profile not found. User is neither a teacher nor a student.",
            status.HTTP_404_NOT_FOUND,
        )


