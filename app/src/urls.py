from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app.src.views import (
    TeacherAssignmentView,
    TeacherSubmissionListView,
    TeacherScoreView,
    StudentAssignmentView,
    StudentSubmitView,
    StudentScoreView,
)

urlpatterns = [
    # JWT auth endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Teacher endpoints
    path('teacher/assignments/', TeacherAssignmentView.as_view(), name='teacher_assignments'),
    path('teacher/assignments/<int:assignment_id>/submissions/', TeacherSubmissionListView.as_view(), name='teacher_submissions'),
    path('teacher/submissions/<int:submission_id>/score/', TeacherScoreView.as_view(), name='teacher_score'),

    # Student endpoints
    path('student/assignments/', StudentAssignmentView.as_view(), name='student_assignments'),
    path('student/assignments/<int:assignment_id>/submit/', StudentSubmitView.as_view(), name='student_submit'),
    path('student/scores/', StudentScoreView.as_view(), name='student_scores'),
]