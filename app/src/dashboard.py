from app.src.models import Teacher, Student, Room, Subject, Year


def dashboard_callback(request, context):
    context.update(
        {
            "kpi": [
                {
                    "title": "Teachers",
                    "metric": Teacher.objects.count(),
                    "icon": "badge",
                },
                {
                    "title": "Students",
                    "metric": Student.objects.count(),
                    "icon": "person_outline",
                },
                {
                    "title": "Rooms",
                    "metric": Room.objects.count(),
                    "icon": "meeting_room",
                },
                {
                    "title": "Subjects",
                    "metric": Subject.objects.count(),
                    "icon": "menu_book",
                },
                {
                    "title": "Years",
                    "metric": Year.objects.count(),
                    "icon": "calendar_today",
                },
            ],
        }
    )
    return context
