migrate:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

run:
	poetry run python manage.py runserver