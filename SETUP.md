# Database Setup Guide

## Local Database Configuration

The application is configured to connect to a local PostgreSQL database. The default credentials are:
- **Username:** `admin` or `postgres`
- **Password:** `password`
- **Host:** `localhost`
- **Port:** `5432`
- **Database Name:** `savingdb`

### Issues with Connection
If you encounter `password authentication failed`, you must configure your local environment variables to match your actual PostgreSQL credentials.

1.  **Create/Edit `.env` file** in `DataBase2` directory:
    ```ini
    DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/savingdb
    ```
    *Replace `YOUR_USERNAME` and `YOUR_PASSWORD` with your actual Postgres credentials.*

2.  **Initialize the Database**:
    Once the `.env` file is correct, run:
    ```bash
    python seed.py
    ```
    This will create the necessary tables (Users, Activities, Meetings, etc.) and add initial data.

## Jenkins Pipeline

A `Jenkinsfile` has been added to the project root. This pipeline:
1.  Checkouts the code.
2.  Installs requirements.
3.  Runs `verify_models.py` using an **ephemeral SQLite database**.

**Note:** The Jenkins pipeline passes successfully because it uses SQLite for isolation. For local development with the real backend, you MUST fix the Postgres connection as described above.
