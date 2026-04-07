# FastAPI URL Shortener

A lightweight REST API service for shortening long URLs, built with FastAPI and SQLAlchemy.

## Features
* **URL Shortening**: Generates unique 4-character codes for any valid URL.
* **Redirect Service**: Handles redirection from short codes to original destinations.
* **CRUD Operations**: Endpoints to list, search, update, and delete links in the database.
* **Validation**: Automatic URL format checking using Pydantic.
* **Interactive Docs**: Built-in Swagger UI and ReDoc for testing endpoints.

## Tech Stack
* **Language**: Python 3.14.3
* **Framework**: FastAPI
* **ORM**: SQLAlchemy (SQLite)
* **Validation**: Pydantic v2

## Getting Started

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/url-shortener.git](https://github.com/your-username/url-shortener.git)
cd url-shortener
```
### Install Dependencies
```Bash
pip install fastapi uvicorn sqlalchemy pydantic
```
### Run the Server
```Bash
uvicorn main:app --reload
```

### Access Documentation
* Once the server is running, you can explore the API at:
* Swagger UI: http://127.0.0.1:8000/docs
* Redoc: http://127.0.0.1:8000/redoc
