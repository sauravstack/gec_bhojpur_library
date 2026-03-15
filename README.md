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
CREATE DATABASE library_db;
USE library_db;

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

INSERT INTO admins (email, password)
VALUES ('admin@library.com', 'admin123');

CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200),
    author VARCHAR(200),
    isbn VARCHAR(50) UNIQUE,
    category VARCHAR(100),
    quantity INT
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150),
    email VARCHAR(100) UNIQUE
);

CREATE TABLE issued_books (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    user_id INT,
    issue_date DATE,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

SHOW TABLES;

INSERT INTO books (title, author, isbn, category, quantity)
VALUES
('Database Systems', 'Elmasri', '9780133970777', 'Engineering', 5),
('Operating System', 'Galvin', '9781118063330', 'Engineering', 3);

INSERT INTO users (name, email)
VALUES
('karan Kumar','karan@email.com'),
('saurav sharma','saurav@email.com'),
('manish Kumar','manish@email.com');

SELECT 
users.name AS user_name,
books.title AS book_title,
issued_books.issue_date,
issued_books.return_date
FROM issued_books
JOIN users ON issued_books.user_id = users.user_id
JOIN books ON issued_books.book_id = books.book_id;

SHOW TABLES;
SELECT * FROM books;
SELECT * FROM users;
SELECT * FROM books;
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
