# SAVING_SERVER Database

This directory contains the database implementation for the SAVING_SERVER, using **Docker**, **PostgreSQL**, and **Flask-SQLAlchemy**.

## 📁 Structure

- **`models/`**: SQLAlchemy models defining the database schema.
    - `user.py`: User model (users, roles, profiles).
    - `invite.py`: Invitation codes for managers.
    - `file.py`: File metadata.
- **`docker-compose.yml`**: Docker configuration for the PostgreSQL database.
- **`config/`**: Configuration settings.
- **`app.py`**: Minimal Flask app for database management (migrations, seeding).
- **`seed.py`**: Script to populate the database with initial data.

## 🚀 Quick Start

### 1. Start Database
```bash
docker-compose up -d
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
# Initialize migrations (if not already done)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed data
python seed.py
```

## 📊 Schema

The schema matches the `SAVING_SERVER_API_SPECIFICATION.md`:
- **Users**: Stores user info, roles, and links to auth provider (`user_id`).
- **Invites**: Manager invitation codes.
- **Files**: Metadata for uploaded files.

## 🛠️ Management

Use Flask-Migrate commands to manage schema changes:
- `flask db migrate -m "Message"`: Generate migration.
- `flask db upgrade`: Apply changes.

## ❓ Troubleshooting

### Docker Not Running
If you see connection errors when running `docker-compose up`, ensure **Docker Desktop** is running.

### Verification without Docker
You can run the verification script without Docker, as it uses a local SQLite database for testing:
```bash
python verify_models.py
```
