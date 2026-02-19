migrate:
	poetry run python manage.py make migrations
	poetry run python manage.py migrate

run:
	poetry run python manage.py runserver