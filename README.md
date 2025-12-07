# SAVING_SERVER - User & Meeting Management Service

This is the **SAVING_SERVER**, a Flask-based REST API service for managing users, meetings, files, invitations, and manager promotions. It uses **PostgreSQL**, **Docker**, and **Flask-SQLAlchemy**.

## � Documentation

- **[Complete API Documentation](COMPLETE_API_DOCUMENTATION.md)** - Full reference with examples
- **[API Endpoints Summary](API_ENDPOINTS_SUMMARY.md)** - Quick endpoint reference table
- **[Quick Start Guide](QUICK_START.md)** - Get started quickly
- **[Manager Code API](MANAGER_CODE_API.md)** - Manager promotion system
- **[Meetings API](MEETINGS_API.md)** - Meeting management details

## 🚀 Features

- **User Management** - Create, read, update users with role-based access
- **Meeting Management** - Create meetings with logging and participant tracking
- **File Upload/Download** - Secure file storage and retrieval
- **Invite System** - Manager invitation codes
- **Manager Promotion** - HR-controlled promotion code system
- **Health Monitoring** - Service health and database status endpoints

## 📁 Project Structure

```
nexus/
├── models/           # Database models
│   ├── user.py      # User model with roles
│   ├── meeting.py   # Meeting model with logging
│   ├── file.py      # File metadata
│   ├── invite.py    # Invitation codes
│   └── manager_code.py  # Manager promotion codes
├── routes/          # API endpoints
│   ├── users.py     # User management
│   ├── meetings.py  # Meeting management
│   ├── files.py     # File upload/download
│   ├── invites.py   # Invite codes
│   └── manager_codes.py  # Manager promotions
├── config/          # Configuration
├── utils/           # Security & validators
├── storage/         # File storage
├── app.py           # Main Flask application
└── verify_api.py    # API test suite
```

## 🚀 Quick Start

### 1. Start Database (Docker)
```bash
docker-compose up -d
```

### 2. Install Dependencies
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
# Create tables
flask shell
>>> from models import db
>>> db.create_all()
>>> exit()

# Or use migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Seed Database (Optional)
```bash
python seed.py
```

### 5. Run Server
```bash
python app.py
# Server runs on http://localhost:5001
```

### 6. Test API
```bash
python verify_api.py
```

## � Authentication

All API endpoints require authentication via API key header:

```http
X-Internal-Key: nexus-internal-secret-key-123
```

> Change this in production via the `INTERNAL_API_KEY` environment variable.

## 📡 API Endpoints

### Health & Status
- `GET /` - Service status and DB connection
- `GET /health` - Health check

### Users (`/users`)
- `POST /users/` - Create user
- `GET /users/` - Get all users
- `PUT /users/<email>` - Update user

### Meetings (`/meetings`)
- `POST /meetings/` - Create meeting
- `GET /meetings/` - List meetings
- `GET /meetings/<meeting_id>` - Get meeting
- `PUT /meetings/<meeting_id>` - Update meeting
- `POST /meetings/<meeting_id>/start` - Start meeting
- `POST /meetings/<meeting_id>/end` - End meeting
- `POST /meetings/<meeting_id>/log` - Append log
- `GET /meetings/<meeting_id>/log` - Get log
- `DELETE /meetings/<meeting_id>` - Delete meeting

### Files (`/file`)
- `POST /file/upload` - Upload file
- `GET /file/get/<filename>` - Download file
- `GET /file/getAll` - List files

### Manager Codes (`/manager_codes`)
- `POST /manager_codes/becameManagerCode` - Create promotion code
- `POST /manager_codes/validateBecameManagerCode` - Use promotion code
- `GET /manager_codes/becameManagerCode/<code>` - Get code details
- `GET /manager_codes/becameManagerCode` - List codes

See [API_ENDPOINTS_SUMMARY.md](API_ENDPOINTS_SUMMARY.md) for complete details.

## 💡 Quick Examples

### Create a User
```bash
curl -X POST http://localhost:5001/users/ \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "userID": "auth0_123",
    "role": "employee",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Create a Meeting
```bash
curl -X POST http://localhost:5001/meetings/ \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Standup",
    "created_by": "manager@company.com"
  }'
```

### Upload a File
```bash
curl -X POST http://localhost:5001/file/upload \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -F "file=@document.pdf" \
  -F "user_email=user@company.com"
```

## 🗄️ Database Schema

### Users Table
- Stores user information with roles (hr, manager, employee, guest)
- Links to Auth0 via `user_id`

### Meetings Table
- Meeting metadata with participant tracking
- Automatic log file generation
- Start/end time tracking

### Files Table
- File metadata and storage paths
- User upload tracking

### Manager Codes Table
- HR-controlled promotion codes
- Single-use promotion system
- Audit trail with HR ID

See [Data Models](COMPLETE_API_DOCUMENTATION.md#data-models) for detailed schemas.

## ⚙️ Configuration

Environment variables (`.env` file):

```bash
# Database
DATABASE_URL=postgresql://admin:password@localhost:5432/savingdb

# Security
INTERNAL_API_KEY=nexus-internal-secret-key-123
SECRET_KEY=your-secret-key-here

# File Storage
UPLOAD_FOLDER=./storage/files

# Server
DEBUG=False
```

## � Database Management

Use Flask-Migrate commands to manage schema changes:
- `flask db migrate -m "Message"` - Generate migration
- `flask db upgrade` - Apply changes
- `flask db downgrade` - Rollback changes

Or use Flask shell:
```bash
flask shell
>>> from models import db
>>> db.create_all()  # Create all tables
```

## 🧪 Testing

Run the API test suite:
```bash
python verify_api.py
```

Check specific endpoints:
```bash
curl http://localhost:5001/health
```

## 📦 Dependencies

Main packages:
- Flask - Web framework
- Flask-SQLAlchemy - ORM
- Flask-Migrate - Database migrations
- psycopg2 - PostgreSQL adapter
- python-dotenv - Environment variables

See `requirements.txt` for complete list.

## 🐳 Docker Deployment

The service includes Docker configuration:

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for details.

## 🔐 Security Notes

- Change the default `INTERNAL_API_KEY` in production
- Use strong `SECRET_KEY` for Flask sessions
- Configure database credentials securely
- Limit file upload sizes (default: 10MB)
- Validate all user inputs

## 📋 User Roles

The system supports four user roles:

- **`hr`** - Human Resources (can create promotion codes)
- **`manager`** - Managers (can create invites and meetings)
- **`employee`** - Regular employees
- **`guest`** - Guest users with limited access

## ❓ Troubleshooting

### Docker Not Running
If you see connection errors, ensure **Docker Desktop** is running:
```bash
docker-compose ps
```

### Database Connection Issues
Check your database URL in `.env`:
```bash
DATABASE_URL=postgresql://admin:password@localhost:5432/savingdb
```

### Port Already in Use
If port 5001 is occupied, change it in `app.py`:
```python
app.run(host='0.0.0.0', port=5002, debug=True)
```

### API Key Errors (401)
Ensure you're sending the correct header:
```http
X-Internal-Key: nexus-internal-secret-key-123
```

### File Upload Issues
Check the upload folder exists and has permissions:
```bash
mkdir -p storage/files
```

## 🤝 Integration Examples

### Python
```python
import requests

BASE_URL = "http://localhost:5001"
HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}

# Create user
response = requests.post(
    f"{BASE_URL}/users/",
    headers=HEADERS,
    json={"email": "test@company.com", "userID": "123", ...}
)
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://localhost:5001',
  headers: {'X-Internal-Key': 'nexus-internal-secret-key-123'}
});

// Create user
const user = await api.post('/users/', {...});
```

See [COMPLETE_API_DOCUMENTATION.md](COMPLETE_API_DOCUMENTATION.md#code-examples) for more examples.

## 📞 Support

For issues or questions:
1. Check the [Complete API Documentation](COMPLETE_API_DOCUMENTATION.md)
2. Review [API Endpoints Summary](API_ENDPOINTS_SUMMARY.md)
3. Run tests: `python verify_api.py`

## 📄 License

This project is part of the integration course work.

## 🎯 Version

**Current Version:** 1.0  
**Last Updated:** December 7, 2025  
**Service Port:** 5001
