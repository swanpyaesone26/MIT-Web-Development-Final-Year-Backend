
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from app.src.models import Teacher, Student, Year, Subject, Room, Assignment, Submission


class TeacherAssignmentTestCase(TestCase):
	"""Test teacher assignment endpoints."""

	def setUp(self):
		self.client = APIClient()
		self.year = Year.objects.create(year_name="Year 1")
		self.subject = Subject.objects.create(subject_name="Math")
		self.user = User.objects.create_user(username='teacher1', password='testpass123')
		self.teacher = Teacher.objects.create(
			user=self.user,
			teacher_name="Mr. Smith",
			subject=self.subject,
			year=self.year
		)
		response = self.client.post('/api/auth/login/', {
			'username': 'teacher1',
			'password': 'testpass123'
		})
		self.token = response.data.get('access', None)
		if self.token:
			self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

	def test_teacher_can_create_assignment(self):
		response = self.client.post('/api/teacher/assignments/', {
			'assignment_name': 'Homework 1',
			'due_date': '2026-03-01T12:00:00Z'
		})
		if response.status_code != status.HTTP_201_CREATED:
			print('Assignment creation error:', response.data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data['assignment_name'], 'Homework 1')

	def test_teacher_can_list_assignments(self):
		Assignment.objects.create(teacher=self.teacher, assignment_name="Test Assignment")
		response = self.client.get('/api/teacher/assignments/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(len(response.data), 1)

	def test_non_teacher_cannot_create_assignment(self):
		other_user = User.objects.create_user(username='random', password='testpass123')
		self.client.force_authenticate(user=other_user)
		response = self.client.post('/api/teacher/assignments/', {
			'assignment_name': 'Hack Assignment',
		})
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StudentAssignmentTestCase(TestCase):
	"""Test student assignment endpoints."""

	def setUp(self):
		self.client = APIClient()
		self.year = Year.objects.create(year_name="Year 2")
		self.subject = Subject.objects.create(subject_name="Myanmar")
		self.teacher_user = User.objects.create_user(username='teacher2', password='testpass123')
		self.teacher = Teacher.objects.create(
			user=self.teacher_user,
			teacher_name="Ms. Aye",
			subject=self.subject,
			year=self.year
		)
		self.room = Room.objects.create(
			room_name="Myanmar-Y2",
			teacher=self.teacher,
			subject=self.subject,
			year=self.year
		)
		self.student_user = User.objects.create_user(username='student1', password='testpass123')
		self.student = Student.objects.create(
			user=self.student_user,
			student_name="Aung Aung",
			year=self.year
		)
		self.student.rooms.add(self.room)
		self.assignment = Assignment.objects.create(
			teacher=self.teacher,
			assignment_name="Essay 1"
		)
		response = self.client.post('/api/auth/login/', {
			'username': 'student1',
			'password': 'testpass123'
		})
		self.token = response.data.get('access', None)
		if self.token:
			self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

	def test_student_can_view_assignments(self):
		response = self.client.get('/api/student/assignments/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(len(response.data), 1)

	def test_student_cannot_submit_twice(self):
		Submission.objects.create(
			assignment=self.assignment,
			student=self.student,
			file='submissions/test.pdf'
		)
		response = self.client.post(
			f'/api/student/assignments/{self.assignment.assignment_id}/submit/',
			{'file': 'dummy'},
			format='multipart'
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
