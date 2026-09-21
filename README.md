# Retrogames Authentication Service

A lightweight, robust backend authentication service for RetroGames built with **Python**, **Flask**, and **Flask-SQLAlchemy**.

This service replaces the previous Node.js/Express implementation, providing `/register` and `/login` endpoints with secure password hashing (`bcrypt`) and SQLite persistence.

---

## 🛠️ Tech Stack

- **Python 3**
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM and database management
- **Flask-CORS**: Cross-Origin Resource Sharing support for frontend integration
- **bcrypt**: Secure password hashing with salt rounds
- **SQLite**: Local relational database (`auth.db`)

---

## 📂 Project Structure

```
retrogames-service/
├── app.py              # Application factory and entry point
├── config.py           # Configuration (Database URI, secret key, port)
├── models.py           # SQLAlchemy User and GameScore models
├── routes.py           # Auth and score routes
├── requirements.txt    # Python dependencies
├── tests/
│   ├── test_auth.py    # Auth unit & integration tests
│   └── test_scores.py  # Score unit & integration tests
└── README.md           # Documentation
```

---

## 🚀 Setup & Installation

### 1. Create a Virtual Environment

```bash
cd /home/chunyi/Documents/retrogames-service
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Service

```bash
python app.py
```
By default, the server runs at `http://localhost:3000`.

To customize the port or database URL:
```bash
PORT=5000 DATABASE_URL=sqlite:///auth.db python app.py
```

---

## 📡 API Endpoints

### 1. Register User
- **Method:** `POST`
- **Path:** `/register`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "email": "player1@retro.net",
    "password": "securePassword123"
  }
  ```
- **Responses:**
  - `201 Created`:
    ```json
    {
      "message": "User registered successfully!",
      "userId": 1
    }
    ```
  - `400 Bad Request` (Missing fields or duplicate email):
    ```json
    {
      "error": "Email and password are required."
    }
    ```
    or
    ```json
    {
      "error": "Email already exists."
    }
    ```
  - `500 Internal Server Error`:
    ```json
    {
      "error": "Database error."
    }
    ```

---

### 2. Login User
- **Method:** `POST`
- **Path:** `/login`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "email": "player1@retro.net",
    "password": "securePassword123"
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "message": "Login successful!",
      "user": {
        "id": 1,
        "email": "player1@retro.net"
      }
    }
    ```
  - `400 Bad Request` (Missing fields):
    ```json
    {
      "error": "Email and password are required."
    }
    ```
  - `401 Unauthorized` (Wrong credentials or non-existent user):
    ```json
    {
      "error": "Invalid email or password."
    }
    ```

---

### 3. Record Game Score
- **Method:** `POST`
- **Path:** `/scores`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "userId": 1,
    "gameId": "pacman",
    "score": 1500
  }
  ```
  *(Both camelCase `userId`/`gameId` and snake_case `user_id`/`game_id` are supported)*
- **Responses:**
  - `201 Created`:
    ```json
    {
      "message": "Score recorded successfully!",
      "score": {
        "id": 1,
        "userId": 1,
        "gameId": "pacman",
        "score": 1500,
        "createdAt": "2026-09-21T23:00:00.000000+00:00"
      }
    }
    ```
  - `400 Bad Request` (Missing fields or invalid score value):
    ```json
    {
      "error": "userId, gameId, and score are required."
    }
    ```
  - `404 Not Found` (User does not exist):
    ```json
    {
      "error": "User not found."
    }
    ```

---

### 4. Get Game Scores / Leaderboard
- **Method:** `GET`
- **Path:** `/scores/<game_id>` or `/scores/leaderboard/<game_id>`
- **Query Parameters:** `limit` (optional, integer limit on number of results)
- **Responses:**
  - `200 OK`:
    ```json
    {
      "gameId": "pacman",
      "scores": [
        {
          "id": 2,
          "userId": 2,
          "gameId": "pacman",
          "score": 3000,
          "createdAt": "2026-09-21T23:00:00.000000+00:00"
        },
        {
          "id": 1,
          "userId": 1,
          "gameId": "pacman",
          "score": 1500,
          "createdAt": "2026-09-21T22:30:00.000000+00:00"
        }
      ]
    }
    ```

---

### 5. Get User Scores
- **Method:** `GET`
- **Path:** `/users/<user_id>/scores`
- **Responses:**
  - `200 OK`:
    ```json
    {
      "userId": 1,
      "scores": [
        {
          "id": 1,
          "userId": 1,
          "gameId": "pacman",
          "score": 1500,
          "createdAt": "2026-09-21T23:00:00.000000+00:00"
        }
      ]
    }
    ```
  - `404 Not Found` (User does not exist):
    ```json
    {
      "error": "User not found."
    }
    ```

---

### 6. Health Check
- **Method:** `GET`
- **Path:** `/health`
- **Response:**
  - `200 OK`: `{"status": "healthy"}`

---

## 🧪 Running Tests

```bash
pytest tests/
```
