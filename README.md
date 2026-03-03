# MIT-Web-Development-Final-Year-Backend

## Project Overview

A School Management System backend for organizing class schedules, assignments, and submissions. Built with Django and PostgreSQL, designed for small and medium-sized schools.

## Prerequisites

- Python 3.12+
- Poetry
- PostgreSQL

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/MIT-Web-Development-Final-Year-Backend.git
   cd MIT-Web-Development-Final-Year-Backend
   ```
2. Install Poetry:
   ```bash
   pip install poetry
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```
4. Create a `.env` file in the root directory and add your configuration (see `.env.example`).

## Usage

- **Migrate database:**
  ```bash
  make migrate
  ```
- **Run development server:**
  ```bash
  make run
  ```
- **Create superuser:**
  ```bash
  poetry run python manage.py createsuperuser
  ```

## Project Structure

```
MIT-Web-Development-Final-Year-Backend/
├── app/                # Django application
│   ├── config/         # Project settings and config
│   └── src/            # Main app logic (models, views, etc.)
├── manage.py           # Django management script
├── Makefile            # Build automation commands
├── pyproject.toml      # Poetry dependencies
├── .env.example        # Environment variable template
└── README.md           # Project info
```

## Main URLs

- **Admin Panel:** `http://127.0.0.1:8000/admin/`
- **API Root:** `http://127.0.0.1:8000/api/`

## Technologies Used

- Django 6.x
- Django REST Framework
- PostgreSQL
- Poetry
- Python-dotenv
- Django-filter

## License

See LICENSE file for details.
