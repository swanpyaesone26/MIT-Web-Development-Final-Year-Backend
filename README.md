# MIT-Web-Development-Final-Year-Backend

##Project Overview

This project is a simple School Management System designed to streamline daily operations for small and medium-sized schools. It focuses entirely on organizing class schedules and managing assignments.

## Prerequisites

- Python 3.12 or higher
- Poetry (Python dependency management)
- PostgreSQL database 

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/MIT-Web-Development-Final-Year-Backend.git
   cd MIT-Web-Development-Final-Year-Backend
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   pip install poetry
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your configuration:

## Running the Project

### Using Makefile Commands (Recommended)

1. **Set up database:**
   ```bash
   make migrate
   ```

2. **Run the development server:**
   ```bash
   make run
   ```

## Project Structure

```
MIT-Web-Development-Final-Year-Backend/
├── app/                    # Django application directory
│   ├── app/               # Main Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py    # Django settings
│   │   ├── urls.py        # URL configuration
│   │   ├── wsgi.py        # WSGI configuration
│   │   └── asgi.py        # ASGI configuration
├── manage.py              # Django management script
├── pyproject.toml         # Poetry configuration and dependencies
├── Makefile              # Build automation commands
└── README.md             
```

## Available URLs

Once the server is running, you can access:

- **Admin Panel:** `http://127.0.0.1:8000/admin/` (requires superuser)
- **API Root:** `http://127.0.0.1:8000/api/` (if API endpoints are configured)

## Technologies Used

- **Django 6.0+** - Web framework
- **Django REST Framework** - REST API toolkit
- **PostgreSQL** - Database (via psycopg2-binary)
- **Poetry** - Dependency management
- **Python-dotenv** - Environment variable management
- **Django-filter** - Filtering support for APIs

## Development

This is the 4th year of the final project for website development subject contributed by 3 members.

## License

This project is licensed under the terms specified in the LICENSE file.
