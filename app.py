from datetime import date
from pathlib import Path

import mysql.connector
from mysql.connector import Error

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

app = FastAPI(title="GEC Library API")

# ✅ Added CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

_db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Saurav@2005",
    "database": "library_db",
    "connection_timeout": 2
}

_db = mysql.connector.connect(**_db_config)
_db.autocommit = True


def get_cursor():
    global _db
    try:
        if not _db.is_connected():
            _db = mysql.connector.connect(**_db_config)
            _db.autocommit = True
        _db.ping(reconnect=True, attempts=1, delay=0)
    except Error:
        _db = mysql.connector.connect(**_db_config)
        _db.autocommit = True

    return _db.cursor(dictionary=True)


# ── Pydantic models ─────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class BookRequest(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    quantity: int


class UserRequest(BaseModel):
    name: str
    email: str


class IssueRequest(BaseModel):
    book_id: int
    user_id: int


class ReturnRequest(BaseModel):
    book_id: int
    user_id: int


# ── Pages ──────────────────────────────────────────────────

@app.get("/")
def get_login_page():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/dashboard.html")
def get_dashboard_page():
    return FileResponse(BASE_DIR / "dashboard.html")


# ── Login ──────────────────────────────────────────────────

@app.post("/api/login")
def login(payload: LoginRequest):
    cursor = get_cursor()
    cursor.execute(
        "SELECT * FROM admins WHERE email=%s AND password=%s",
        (payload.email, payload.password),
    )
    user = cursor.fetchone()
    cursor.close()

    if user:
        return {
            "access_token": "demo-token-123",
            "token_type": "bearer",
            "user_email": payload.email
        }

    raise HTTPException(status_code=401, detail="Invalid email or password")


# ── Stats ──────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    cursor = get_cursor()

    cursor.execute("SELECT COALESCE(SUM(quantity),0) AS total FROM books")
    total_books = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM issued_books WHERE return_date IS NULL")
    issued = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM users")
    total_users = cursor.fetchone()["cnt"]

    cursor.close()

    return {
        "total_books": int(total_books),
        "available": max(0, int(total_books) - int(issued)),
        "issued": int(issued),
        "users": int(total_users),
    }


@app.get("/api/dashboard-data")
def get_dashboard_data():
    cursor = get_cursor()

    cursor.execute("SELECT COALESCE(SUM(quantity),0) AS total FROM books")
    total_books = int(cursor.fetchone()["total"])

    cursor.execute("SELECT COUNT(*) AS cnt FROM issued_books WHERE return_date IS NULL")
    issued = int(cursor.fetchone()["cnt"])

    cursor.execute("SELECT COUNT(*) AS cnt FROM users")
    total_users = int(cursor.fetchone()["cnt"])

    cursor.execute("SELECT book_id,title,author,isbn,category,quantity FROM books ORDER BY title")
    books = cursor.fetchall()

    cursor.execute("SELECT user_id,name,email FROM users ORDER BY name")
    users = cursor.fetchall()

    cursor.close()

    return {
        "stats": {
            "total_books": total_books,
            "available": max(0, total_books - issued),
            "issued": issued,
            "users": total_users,
        },
        "books": books,
        "users": users,
    }


# ── Books ──────────────────────────────────────────────────

@app.get("/api/books")
def list_books():
    cursor = get_cursor()
    cursor.execute("SELECT book_id,title,author,isbn,category,quantity FROM books ORDER BY title")
    books = cursor.fetchall()
    cursor.close()
    return books


@app.post("/api/books")
def add_book(payload: BookRequest):
    cursor = get_cursor()
    try:
        cursor.execute(
            "INSERT INTO books (title,author,isbn,category,quantity) VALUES (%s,%s,%s,%s,%s)",
            (payload.title, payload.author, payload.isbn, payload.category, payload.quantity),
        )
        _db.commit()
    except Error as e:
        _db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

    return {"message": "Book added successfully"}


# ── Users ──────────────────────────────────────────────────

@app.get("/api/users")
def list_users():
    cursor = get_cursor()
    cursor.execute("SELECT user_id,name,email FROM users ORDER BY name")
    users = cursor.fetchall()
    cursor.close()
    return users


@app.post("/api/users")
def add_user(payload: UserRequest):
    cursor = get_cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name,email) VALUES (%s,%s)",
            (payload.name, payload.email),
        )
        _db.commit()
    except Error as e:
        _db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

    return {"message": "User created successfully"}


# ── Issue Book ─────────────────────────────────────────────

@app.post("/api/issue")
def issue_book(payload: IssueRequest):
    cursor = get_cursor()
    try:
        cursor.execute("SELECT quantity FROM books WHERE book_id=%s", (payload.book_id,))
        book = cursor.fetchone()

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM issued_books WHERE book_id=%s AND return_date IS NULL",
            (payload.book_id,),
        )

        if cursor.fetchone()["cnt"] >= book["quantity"]:
            raise HTTPException(status_code=400, detail="No copies available")

        cursor.execute(
            "INSERT INTO issued_books (book_id,user_id,issue_date) VALUES (%s,%s,%s)",
            (payload.book_id, payload.user_id, date.today()),
        )

        _db.commit()

    except HTTPException:
        raise
    except Error as e:
        _db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

    return {"message": "Book issued successfully"}


# ── Return Book ────────────────────────────────────────────

@app.post("/api/return")
def return_book(payload: ReturnRequest):
    cursor = get_cursor()

    try:
        cursor.execute(
            "UPDATE issued_books SET return_date=%s "
            "WHERE book_id=%s AND user_id=%s AND return_date IS NULL "
            "ORDER BY issue_date ASC LIMIT 1",
            (date.today(), payload.book_id, payload.user_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No active issue found")

        _db.commit()

    except HTTPException:
        raise
    except Error as e:
        _db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

    return {"message": "Book returned successfully"}