migrate:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

run:
	poetry run python manage.py runserver

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up

docker-up-build:
	docker-compose up --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec web bash

docker-migrate:
	docker-compose exec web python manage.py migrate

docker-createsuperuser:
	docker-compose exec web python manage.py createsuperuser

docker-test:
	docker-compose exec web python manage.py test

# Clean up
docker-clean:
	docker-compose down -v
	docker system prune -f