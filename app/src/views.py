from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from app.src.models import Assignment, Submission, Teacher, Student, Room
from app.src.serializers import AssignmentSerializer, SubmissionSerializer


# Teacher Views

class TeacherAssignmentView(APIView):
    """Teacher can get the list of their assignments and create new assignments."""
    permission_classes = [IsAuthenticated]

    # if teacher is authenticated, get all assignments for that teacher
    def get(self, request):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return Response({'error': 'You are not a teacher.'}, status=status.HTTP_403_FORBIDDEN)

        assignments = Assignment.objects.filter(teacher=teacher)
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    # if teacher is authenticated, create a new assignment for that teacher
    def post(self, request):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return Response({'error': 'You are not a teacher.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=teacher)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherSubmissionListView(APIView):
    """Teacher can view all submissions for a specific assignment."""
    permission_classes = [IsAuthenticated]

    # check if teacher is authenticated, verify that assignment is belong to that teacher, get the assignment that belong to the requested teacher
    def get(self, request, assignment_id):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return Response({'error': 'You are not a teacher.'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure the assignment belongs to this teacher
        try:
            assignment = Assignment.objects.get(assignment_id=assignment_id, teacher=teacher)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

        submissions = Submission.objects.filter(assignment=assignment)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class TeacherScoreView(APIView):
    """Teacher can give score to a submission."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, submission_id):
        try:
            teacher = request.user.teacher
        except Teacher.DoesNotExist:
            return Response({'error': 'You are not a teacher.'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure the submission belongs to this teacher's assignment
        try:
            submission = Submission.objects.get(
                submission_id=submission_id,
                assignment__teacher=teacher
            )
        except Submission.DoesNotExist:
            return Response({'error': 'Submission not found.'}, status=status.HTTP_404_NOT_FOUND)

        score = request.data.get('score')
        if score is None:
            return Response({'error': 'Score is required.'}, status=status.HTTP_400_BAD_REQUEST)

        submission.score = score
        submission.save()
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)


# Student Views

class StudentAssignmentView(APIView):
    """Student can view assignments for their rooms."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return Response({'error': 'You are not a student.'}, status=status.HTTP_403_FORBIDDEN)

        # Get all rooms the student belongs to
        student_rooms = student.rooms.all()
        # Get teachers who own those rooms
        teachers = Teacher.objects.filter(room__in=student_rooms)
        # Get assignments from those teachers
        assignments = Assignment.objects.filter(teacher__in=teachers)
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class StudentSubmitView(APIView):
    """Student can submit a file for an assignment."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, assignment_id):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return Response({'error': 'You are not a student.'}, status=status.HTTP_403_FORBIDDEN)

        # Check the assignment exists and belongs to a room the student is in
        student_rooms = student.rooms.all()
        teachers = Teacher.objects.filter(room__in=student_rooms)
        try:
            assignment = Assignment.objects.get(assignment_id=assignment_id, teacher__in=teachers)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if student already submitted
        if Submission.objects.filter(assignment=assignment, student=student).exists():
            return Response({'error': 'You have already submitted this assignment.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assignment=assignment, student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentScoreView(APIView):
    """Student can view their own scores."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return Response({'error': 'You are not a student.'}, status=status.HTTP_403_FORBIDDEN)

        submissions = Submission.objects.filter(student=student)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


