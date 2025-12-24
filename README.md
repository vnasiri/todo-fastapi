# Todos FastAPI
A modern, secure, and scalable To-Do application built with FastAPI. This project provides a full-featured backend API with authentication, authorization, and CRUD operations for users and tasks. It incorporates asynchronous database interactions, background task processing for email verification, and a responsive frontend built purely with HTML, CSS, and JavaScript. The application follows best practices for security, performance, and maintainability, including rate limiting, secure password hashing, and JWT-based authentication.

## Features
- Full Authentication and Authorization: Secure user registration, login, email verification, and role-based access control using JWT tokens.
- CRUD Operations: Complete create, read, update, and delete functionality for users and to-do items.
- Background Tasks: Utilizes Celery for asynchronous processing, such as sending email verification links via fastapi-mail.
- In-Memory Caching: Redis integration for fast, in-memory data storage and caching.
- Database Management: Asynchronous interactions with PostgreSQL using SQLModel, with migrations handled by Alembic.
- Frontend UI: A clean, interactive user interface built with vanilla HTML, CSS, and JavaScript, served directly from FastAPI templates using Jinja2.
- Security Best Practices: Includes rate limiting, exception handling, secure password storage, and middleware for CORS and logging.
- Monitoring and Testing: Flower for Celery task monitoring and comprehensive unit tests with pytest.
- Containerization: Fully Dockerized for easy deployment and development consistency.

## Technologies Used
- Backend Framework: FastAPI (for high-performance API development)
- Database ORM: Async SQLModel (for asynchronous SQL interactions)
- Database: PostgreSQL (persistent storage)
- Migrations: Alembic (database schema management)
- Caching: Redis (in-memory database)
- Task Queue: Celery (background task processing)
- Task Monitoring: Flower (Celery dashboard)
- Email Integration: fastapi-mail (with Jinja2 for templated emails)
- Testing: pytest (unit and integration tests)
- Containerization: Docker (for development and production environments)
- Other: Jinja2 (templating), HTML/CSS/JS (frontend)

## Project Structure
The project is organized for modularity and scalability. Below is the directory structure:
```
todos-fastapi/
├── src
│   ├── api
│   │   ├── v1
│   │   │   ├── routers.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── auth
│   │   ├── controller.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── exceptions.py
│   │   └── __init__.py
│   ├── core
│   │   ├── repositories
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── todo.py
│   │   │   └── __init__.py
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── database
│   │   ├── db.py
│   │   ├── redis.py
│   │   └── __init__.py
│   ├── entities
│   │   ├── todo.py
│   │   ├── user.py
│   │   └── __init__.py
│   ├── todos
│   │   ├── controller.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── exceptions.py
│   │   └── __init__.py
│   ├── users
│   │   ├── controller.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── exceptions.py
│   │   └── __init__.py
│   ├── tests
│   │   ├── conftest.py
│   │   ├── test_todos.py
│   │   ├── test_users.py
│   │   └── __init__.py
│   ├── worker
│   │   ├── tasks.py
│   │   └── __init__.py
│   ├── static
│   │   ├── css
│   │   ├── img
│   │   └── js
│   ├── templates
│   │   ├── emails
│   │   │   └── verify_email.html
│   │   ├── base.html
│   │   ├── index.html
│   │   └── ...
│   ├── dependencies.py
│   ├── main.py
│   ├── logs.py
│   ├── rate_limiting.py
│   ├── middleware.py
│   ├── frontend_router.py
│   ├── exceptions.py
│   ├── tags.py
│   └── __init__.py
├── templates
├── static
├── alembic
│   └── alembic.ini
├── compose.yaml
├── .gitignore
├── .dockerignore
├── compose.yaml
├── Dockerfile
├── .env
├── entrypoint.sh
├── Makefile
├── pyproject.toml
├── uv.lock
└── .python-version
```
