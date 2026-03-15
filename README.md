# GEC Bhojpur Library Management System

A simple, fast library management web app built with FastAPI + MySQL.

## Features

- Admin login
- Dashboard with live stats
- Books inventory management
- Member registration
- Issue and return workflow
- Single-call dashboard API for faster loading (`/api/dashboard-data`)

## Tech Stack

- Backend: FastAPI
- Frontend: HTML, CSS, JavaScript
- Database: MySQL
- Server: Uvicorn

## Project Structure

```text
app.py
index.html
dashboard.html
requirements.txt
```

## Requirements

- Python 3.10+
- MySQL Server

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Database Setup

Create a MySQL database named `library_db`, then run the following SQL:

```sql
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

CREATE TABLE IF NOT EXISTS admins (
  admin_id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
  book_id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  isbn VARCHAR(100) NOT NULL,
  category VARCHAR(120) NOT NULL,
  quantity INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS issued_books (
  issue_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT NOT NULL,
  user_id INT NOT NULL,
  issue_date DATE NOT NULL,
  return_date DATE NULL,
  FOREIGN KEY (book_id) REFERENCES books(book_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

INSERT INTO admins (email, password)
VALUES ('admin@library.com', 'admin123')
ON DUPLICATE KEY UPDATE email = email;
```

## Configuration

Database config is currently hardcoded in `app.py`:

- host: `localhost`
- user: `root`
- password: `Saurav@2005`
- database: `library_db`

Update these values in `app.py` to match your local setup.

## Run the App

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open in browser:

- Login page: `http://127.0.0.1:8000/`
- Dashboard: `http://127.0.0.1:8000/dashboard.html`

## API Endpoints

- `POST /api/login`
- `GET /api/stats`
- `GET /api/dashboard-data`
- `GET /api/books`
- `POST /api/books`
- `GET /api/users`
- `POST /api/users`
- `POST /api/issue`
- `POST /api/return`

## Notes

- Login token is demo-style and stored in browser localStorage.
- CORS is currently open to all origins.
- For production, move DB credentials to environment variables and hash passwords.
