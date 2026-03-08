from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app.src.views import (
    TeacherAssignmentView,
    TeacherAssignmentDetailView,
    TeacherAssignmentCloseView,
    TeacherSubmissionListView,
    TeacherScoreView,
    StudentAssignmentView,
    StudentSubmitView,
    StudentScoreView,
    UserProfileView,
)

urlpatterns = [
    # JWT auth endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),

    # Teacher endpoints
    path('teacher/assignments/', TeacherAssignmentView.as_view(), name='teacher_assignments'),
    path('teacher/assignments/<int:assignment_id>/', TeacherAssignmentDetailView.as_view(), name='teacher_assignment_detail'),
    path('teacher/assignments/<int:assignment_id>/close/', TeacherAssignmentCloseView.as_view(), name='teacher_assignment_close'),
    path('teacher/assignments/<int:assignment_id>/submissions/', TeacherSubmissionListView.as_view(), name='teacher_submissions'),
    path('teacher/submissions/<int:submission_id>/score/', TeacherScoreView.as_view(), name='teacher_score'),

    # Student endpoints
    path('student/assignments/', StudentAssignmentView.as_view(), name='student_assignments'),
    path('student/assignments/<int:assignment_id>/submit/', StudentSubmitView.as_view(), name='student_submit'),
    path('student/scores/', StudentScoreView.as_view(), name='student_scores'),
]