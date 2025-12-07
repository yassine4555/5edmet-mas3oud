# SAVING_SERVER - Complete API Documentation

**Version:** 1.0  
**Base URL:** `http://localhost:5001`  
**Service Name:** SAVING_SERVER  
**Last Updated:** December 7, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management API](#user-management-api)
3. [Invite Management API](#invite-management-api)
4. [File Management API](#file-management-api)
5. [Meeting Management API](#meeting-management-api)
6. [Manager Code Promotion API](#manager-code-promotion-api)
7. [Health & Status API](#health--status-api)
8. [Error Responses](#error-responses)
9. [Data Models](#data-models)
10. [Code Examples](#code-examples)

---

## Authentication

All API endpoints require authentication using an API key.

### Headers Required

```http
X-Internal-Key: nexus-internal-secret-key-123
Content-Type: application/json
```

### Default API Key
```
nexus-internal-secret-key-123
```

> ⚠️ **Security Note:** Change this key in production via the `INTERNAL_API_KEY` environment variable.

---

## User Management API

Base Path: `/users`

### 1. Create User

**Endpoint:** `POST /users/`

**Description:** Creates a new user in the system.

**Request Body:**
```json
{
  "email": "john.doe@company.com",
  "userID": "auth0_user_123",
  "role": "employee",
  "first_name": "John",
  "last_name": "Doe",
  "password": "optional_placeholder",
  "department": "Engineering",
  "address": "123 Main St",
  "date_of_birth": "1990-05-15"
}
```

**Required Fields:**
- `email` (string) - Unique email address
- `userID` (string) - Unique user ID from Auth provider
- `role` (string) - One of: `hr`, `manager`, `employee`, `guest`
- `first_name` (string)
- `last_name` (string)

**Optional Fields:**
- `password` (string) - Defaults to "placeholder"
- `department` (string)
- `address` (string)
- `date_of_birth` (string) - Format: YYYY-MM-DD

**Success Response (201):**
```json
{
  "id": 1,
  "email": "john.doe@company.com",
  "userID": "auth0_user_123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "employee",
  "department": "Engineering",
  "address": "123 Main St",
  "date_of_birth": "1990-05-15",
  "employeesList": [],
  "created_at": "2025-12-07T10:30:00Z"
}
```

**Error Responses:**
- `400` - Invalid role
- `409` - Email or UserID already exists
- `422` - Missing required field

---

### 2. Get All Users

**Endpoint:** `GET /users/`

**Description:** Retrieves list of all users.

**Success Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "email": "john.doe@company.com",
      "userID": "auth0_user_123",
      "first_name": "John",
      "last_name": "Doe",
      "role": "employee",
      "department": "Engineering",
      "address": "123 Main St",
      "date_of_birth": "1990-05-15",
      "employeesList": [],
      "created_at": "2025-12-07T10:30:00Z"
    }
  ]
}
```

---

### 3. Update User

**Endpoint:** `PUT /users/<user_id>` or `PATCH /users/<user_id>`

**Description:** Updates user information by email.

**URL Parameters:**
- `user_id` (string) - User's email address (e.g., `john.doe@company.com`)

**Request Body (all fields optional):**
```json
{
  "email": "new.email@company.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "manager",
  "department": "HR",
  "address": "456 Oak Ave",
  "date_of_birth": "1988-03-20",
  "password": "new_placeholder"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "User updated successfully. Updated fields: first_name, department",
  "data": {
    "id": 1,
    "email": "john.doe@company.com",
    "userID": "auth0_user_123",
    "first_name": "Jane",
    "last_name": "Doe",
    "role": "employee",
    "department": "HR",
    "address": "123 Main St",
    "date_of_birth": "1990-05-15",
    "employeesList": [],
    "created_at": "2025-12-07T10:30:00Z"
  }
}
```

**Error Responses:**
- `400` - No valid fields to update
- `404` - User not found

---

## Invite Management API

Base Path: `/invites`

### 1. Create Invite

**Endpoint:** `POST /invites/`

**Description:** Creates an invitation code for a manager to invite employees.

**Request Body:**
```json
{
  "manager_id": "auth0_manager_123",
  "code": "INVITE2025",
  "max_uses": 5
}
```

**Required Fields:**
- `manager_id` (string) - User ID of the manager
- `code` (string) - Unique invitation code

**Optional Fields:**
- `max_uses` (integer) - Maximum number of uses (default: 1)

**Success Response (201):**
```json
{
  "id": 1,
  "manager_id": "auth0_manager_123",
  "code": "INVITE2025",
  "max_uses": 5,
  "used_count": 0,
  "is_active": true,
  "expires_at": "2025-12-14T10:30:00Z",
  "created_at": "2025-12-07T10:30:00Z"
}
```

**Error Responses:**
- `403` - User is not authorized to create invites
- `404` - Manager not found
- `409` - Code already exists
- `422` - Missing manager_id or code

---

## File Management API

Base Path: `/file`

### 1. Upload File

**Endpoint:** `POST /file/upload`

**Description:** Uploads a file to the server.

**Request Type:** `multipart/form-data`

**Form Fields:**
- `file` (file) - The file to upload
- `user_email` (string) - Email of the user uploading

**Success Response (200):**
```json
{
  "success": true,
  "filename": "document.pdf",
  "file_id": "file_a1b2c3d4e5f6",
  "url": "/file/get/document.pdf"
}
```

**Error Responses:**
- `400` - No file part or no selected file
- `404` - User not found

**cURL Example:**
```bash
curl -X POST http://localhost:5001/file/upload \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -F "file=@/path/to/document.pdf" \
  -F "user_email=john.doe@company.com"
```

---

### 2. Download File

**Endpoint:** `GET /file/get/<filename>`

**Description:** Downloads a file from the server.

**URL Parameters:**
- `filename` (string) - Name of the file to download

**Success Response (200):**
- Returns file as attachment

**Error Response:**
- `404` - File not found

---

### 3. Get All Files

**Endpoint:** `GET /file/getAll`

**Description:** Retrieves list of all uploaded files, optionally filtered by user.

**Query Parameters:**
- `user_email` (optional) - Filter files by uploader email

**Success Response (200):**
```json
{
  "files": [
    {
      "id": 1,
      "file_id": "file_a1b2c3d4e5f6",
      "filename": "document.pdf",
      "original_filename": "document.pdf",
      "size": 1024000,
      "content_type": "application/pdf",
      "uploaded_by": "john.doe@company.com",
      "uploaded_at": "2025-12-07T10:30:00Z"
    }
  ]
}
```

**Example:**
```bash
# Get all files
GET /file/getAll

# Get files uploaded by specific user
GET /file/getAll?user_email=john.doe@company.com
```

---

## Meeting Management API

Base Path: `/meetings`

### 1. Create Meeting

**Endpoint:** `POST /meetings/`

**Description:** Creates a new meeting.

**Request Body:**
```json
{
  "title": "Team Standup",
  "object": "Daily sync",
  "description": "Discuss project progress",
  "created_by": "manager@company.com",
  "password": "meeting123",
  "invited_employees": ["emp1@company.com", "emp2@company.com"]
}
```

**Required Fields:**
- `title` (string)
- `created_by` (string) - Email of meeting creator

**Optional Fields:**
- `object` (string) - Meeting objective
- `description` (string)
- `password` (string) - Meeting password
- `invited_employees` (array) - List of invited employee emails

**Success Response (201):**
```json
{
  "id": 1,
  "meeting_id": "mtg_abc123def456",
  "title": "Team Standup",
  "object": "Daily sync",
  "description": "Discuss project progress",
  "created_by": "manager@company.com",
  "password": "meeting123",
  "invitation_link": "http://localhost:5001/join/mtg_abc123def456",
  "invited_employees_list": ["emp1@company.com", "emp2@company.com"],
  "is_active": true,
  "started_at": null,
  "ended_at": null,
  "created_at": "2025-12-07T10:30:00Z",
  "log_path": "./storage/meeting_logs/meeting_mtg_abc123def456_20251207_103000.log"
}
```

---

### 2. Get All Meetings

**Endpoint:** `GET /meetings/`

**Description:** Retrieves meetings, optionally filtered by user or status.

**Query Parameters:**
- `user_email` (optional) - Get meetings created by or involving this user
- `is_active` (optional) - Filter by active status (true/false)

**Success Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "meeting_id": "mtg_abc123def456",
      "title": "Team Standup",
      "created_by": "manager@company.com",
      "is_active": true,
      "created_at": "2025-12-07T10:30:00Z"
    }
  ]
}
```

---

### 3. Get Meeting by ID

**Endpoint:** `GET /meetings/<meeting_id>`

**Description:** Retrieves details of a specific meeting.

**URL Parameters:**
- `meeting_id` (string) - Meeting identifier

**Success Response (200):**
```json
{
  "id": 1,
  "meeting_id": "mtg_abc123def456",
  "title": "Team Standup",
  "object": "Daily sync",
  "description": "Discuss project progress",
  "created_by": "manager@company.com",
  "invitation_link": "http://localhost:5001/join/mtg_abc123def456",
  "invited_employees_list": ["emp1@company.com"],
  "is_active": true,
  "created_at": "2025-12-07T10:30:00Z"
}
```

**Error Response:**
- `404` - Meeting not found

---

### 4. Update Meeting

**Endpoint:** `PUT /meetings/<meeting_id>`

**Description:** Updates meeting details.

**Request Body (all fields optional):**
```json
{
  "title": "Updated Title",
  "object": "New objective",
  "description": "Updated description",
  "password": "newpass123",
  "invited_employees": ["emp3@company.com"],
  "is_active": false
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "meeting_id": "mtg_abc123def456",
  "title": "Updated Title",
  "is_active": false
}
```

---

### 5. Start Meeting

**Endpoint:** `POST /meetings/<meeting_id>/start`

**Description:** Marks a meeting as started and logs the start time.

**Success Response (200):**
```json
{
  "id": 1,
  "meeting_id": "mtg_abc123def456",
  "started_at": "2025-12-07T11:00:00Z",
  "is_active": true
}
```

---

### 6. End Meeting

**Endpoint:** `POST /meetings/<meeting_id>/end`

**Description:** Marks a meeting as ended and calculates duration.

**Success Response (200):**
```json
{
  "id": 1,
  "meeting_id": "mtg_abc123def456",
  "started_at": "2025-12-07T11:00:00Z",
  "ended_at": "2025-12-07T12:00:00Z",
  "is_active": false
}
```

---

### 7. Append Meeting Log

**Endpoint:** `POST /meetings/<meeting_id>/log`

**Description:** Adds a log entry to the meeting log file.

**Request Body:**
```json
{
  "log_entry": "User joined the meeting"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Log entry added"
}
```

**Error Responses:**
- `400` - Meeting has no log path
- `404` - Meeting not found
- `422` - log_entry is required

---

### 8. Get Meeting Log

**Endpoint:** `GET /meetings/<meeting_id>/log`

**Description:** Retrieves meeting log content or downloads log file.

**Query Parameters:**
- `download` (optional) - Set to "true" to download file

**Success Response (200) - Content:**
```json
{
  "meeting_id": "mtg_abc123def456",
  "log_path": "./storage/meeting_logs/meeting_mtg_abc123def456.log",
  "log_content": "Meeting Log: Team Standup\n[2025-12-07 11:00:00] Meeting started\n"
}
```

**Success Response (200) - Download:**
- Returns log file as attachment

---

### 9. Delete Meeting

**Endpoint:** `DELETE /meetings/<meeting_id>`

**Description:** Soft deletes a meeting by marking it as inactive.

**Success Response (200):**
```json
{
  "success": true,
  "message": "Meeting deleted"
}
```

---

## Manager Code Promotion API

Base Path: `/manager_codes`

### 1. Save Manager Promotion Code

**Endpoint:** `POST /manager_codes/becameManagerCode`

**Description:** Creates a code that HR can use to promote employees to managers.

**Request Body:**
```json
{
  "hrid": "hr_user_123",
  "code": "PROMOTE2025",
  "max_uses": 1
}
```

**Required Fields:**
- `hrid` (string) - HR user ID who created the code
- `code` (string) - Unique promotion code

**Optional Fields:**
- `max_uses` (integer) - Maximum uses (default: 1)

**Success Response (201):**
```json
{
  "success": true,
  "message": "Code saved successfully",
  "data": {
    "id": 1,
    "code": "PROMOTE2025",
    "hrid": "hr_user_123",
    "max_uses": 1,
    "used_count": 0,
    "used_by_email": null,
    "is_active": true,
    "created_at": "2025-12-07T10:30:00Z",
    "used_at": null
  }
}
```

**Error Responses:**
- `409` - Code already exists
- `422` - Missing required field

---

### 2. Validate and Use Promotion Code

**Endpoint:** `POST /manager_codes/validateBecameManagerCode`

**Description:** Validates a promotion code and promotes the user to manager.

**Request Body:**
```json
{
  "code": "PROMOTE2025",
  "userMail": "employee@company.com"
}
```

**Required Fields:**
- `code` (string) - Promotion code
- `userMail` (string) - Email of user to promote

**Success Response (200):**
```json
{
  "valid": true,
  "hrid": "hr_user_123",
  "message": "User promoted to manager successfully",
  "user": {
    "id": 5,
    "email": "employee@company.com",
    "role": "manager",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Error Responses:**
- `400` - Code invalid/already used
- `404` - Code or user not found
- `422` - Missing required field

---

### 3. Get Manager Code Details

**Endpoint:** `GET /manager_codes/becameManagerCode/<code>`

**Description:** Retrieves information about a specific promotion code.

**URL Parameters:**
- `code` (string) - The promotion code

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "code": "PROMOTE2025",
    "hrid": "hr_user_123",
    "max_uses": 1,
    "used_count": 1,
    "used_by_email": "employee@company.com",
    "is_active": false,
    "created_at": "2025-12-07T10:30:00Z",
    "used_at": "2025-12-07T11:45:00Z"
  }
}
```

---

### 4. List Manager Codes

**Endpoint:** `GET /manager_codes/becameManagerCode`

**Description:** Lists all promotion codes with optional filtering.

**Query Parameters:**
- `hrid` (optional) - Filter by HR user ID
- `active_only` (optional) - Show only active codes (true/false)

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code": "PROMOTE2025",
      "hrid": "hr_user_123",
      "max_uses": 1,
      "used_count": 0,
      "is_active": true
    }
  ]
}
```

---

## Health & Status API

### 1. Service Status

**Endpoint:** `GET /`

**Description:** Checks if the service and database are running.

**Success Response (200):**
```json
{
  "status": "SAVING_SERVER Ready",
  "db_connection": "OK"
}
```

**Error Response (500):**
```json
{
  "status": "SAVING_SERVER Error",
  "db_connection": "Connection error details"
}
```

---

### 2. Health Check

**Endpoint:** `GET /health`

**Description:** Returns service health status.

**Success Response (200):**
```json
{
  "status": "healthy",
  "service": "SAVING_SERVER",
  "version": "1.0"
}
```

---

## Error Responses

All endpoints use standard HTTP status codes:

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | User not authorized for action |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Missing required fields |
| 500 | Internal Server Error | Server error |

**Standard Error Format:**
```json
{
  "error": "Description of the error"
}
```

**Success Format (for operations):**
```json
{
  "success": true,
  "message": "Operation completed",
  "data": {}
}
```

---

## Data Models

### User Model

```json
{
  "id": 1,
  "email": "user@company.com",
  "userID": "auth0_user_123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "employee",
  "department": "Engineering",
  "address": "123 Main St",
  "date_of_birth": "1990-05-15",
  "employeesList": [],
  "created_at": "2025-12-07T10:30:00Z"
}
```

**Roles:**
- `hr` - Human Resources
- `manager` - Manager
- `employee` - Employee
- `guest` - Guest user

---

### Meeting Model

```json
{
  "id": 1,
  "meeting_id": "mtg_abc123",
  "title": "Team Meeting",
  "object": "Weekly sync",
  "description": "Discuss progress",
  "created_by": "manager@company.com",
  "invitation_link": "http://localhost:5001/join/mtg_abc123",
  "invited_employees_list": ["emp@company.com"],
  "is_active": true,
  "started_at": "2025-12-07T10:00:00Z",
  "ended_at": null,
  "created_at": "2025-12-07T09:00:00Z",
  "log_path": "./storage/meeting_logs/meeting_mtg_abc123.log"
}
```

---

### File Model

```json
{
  "id": 1,
  "file_id": "file_abc123",
  "filename": "document.pdf",
  "original_filename": "document.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "uploaded_by": "user@company.com",
  "uploaded_at": "2025-12-07T10:30:00Z"
}
```

---

## Code Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:5001"
API_KEY = "nexus-internal-secret-key-123"
HEADERS = {
    "X-Internal-Key": API_KEY,
    "Content-Type": "application/json"
}

# Create a user
def create_user():
    response = requests.post(
        f"{BASE_URL}/users/",
        headers=HEADERS,
        json={
            "email": "john.doe@company.com",
            "userID": "auth0_123",
            "role": "employee",
            "first_name": "John",
            "last_name": "Doe",
            "department": "Engineering"
        }
    )
    return response.json()

# Update a user
def update_user(email):
    response = requests.put(
        f"{BASE_URL}/users/{email}",
        headers=HEADERS,
        json={
            "department": "IT",
            "role": "manager"
        }
    )
    return response.json()

# Create a meeting
def create_meeting():
    response = requests.post(
        f"{BASE_URL}/meetings/",
        headers=HEADERS,
        json={
            "title": "Team Standup",
            "created_by": "manager@company.com",
            "invited_employees": ["emp1@company.com"]
        }
    )
    return response.json()

# Upload a file
def upload_file():
    files = {'file': open('document.pdf', 'rb')}
    data = {'user_email': 'john.doe@company.com'}
    response = requests.post(
        f"{BASE_URL}/file/upload",
        headers={"X-Internal-Key": API_KEY},
        files=files,
        data=data
    )
    return response.json()

# Promote user to manager
def promote_to_manager(code, email):
    response = requests.post(
        f"{BASE_URL}/manager_codes/validateBecameManagerCode",
        headers=HEADERS,
        json={
            "code": code,
            "userMail": email
        }
    )
    return response.json()
```

---

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5001';
const API_KEY = 'nexus-internal-secret-key-123';
const headers = {
  'X-Internal-Key': API_KEY,
  'Content-Type': 'application/json'
};

// Create a user
async function createUser() {
  const response = await axios.post(`${BASE_URL}/users/`, {
    email: 'john.doe@company.com',
    userID: 'auth0_123',
    role: 'employee',
    first_name: 'John',
    last_name: 'Doe',
    department: 'Engineering'
  }, { headers });
  return response.data;
}

// Get all users
async function getUsers() {
  const response = await axios.get(`${BASE_URL}/users/`, { headers });
  return response.data;
}

// Create a meeting
async function createMeeting() {
  const response = await axios.post(`${BASE_URL}/meetings/`, {
    title: 'Team Standup',
    created_by: 'manager@company.com',
    invited_employees: ['emp1@company.com']
  }, { headers });
  return response.data;
}

// Start a meeting
async function startMeeting(meetingId) {
  const response = await axios.post(
    `${BASE_URL}/meetings/${meetingId}/start`,
    {},
    { headers }
  );
  return response.data;
}
```

---

### cURL Examples

```bash
# Create a user
curl -X POST http://localhost:5001/users/ \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@company.com",
    "userID": "auth0_123",
    "role": "employee",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Get all users
curl -X GET http://localhost:5001/users/ \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# Update a user
curl -X PUT http://localhost:5001/users/john.doe@company.com \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"department": "IT", "role": "manager"}'

# Create a meeting
curl -X POST http://localhost:5001/meetings/ \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Standup",
    "created_by": "manager@company.com",
    "invited_employees": ["emp1@company.com"]
  }'

# Upload a file
curl -X POST http://localhost:5001/file/upload \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -F "file=@document.pdf" \
  -F "user_email=john.doe@company.com"

# Create manager promotion code
curl -X POST http://localhost:5001/manager_codes/becameManagerCode \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "hrid": "hr_user_123",
    "code": "PROMOTE2025",
    "max_uses": 1
  }'

# Validate and use promotion code
curl -X POST http://localhost:5001/manager_codes/validateBecameManagerCode \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PROMOTE2025",
    "userMail": "employee@company.com"
  }'
```

---

## Quick Reference

### All Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Health & Status** |
| GET | `/` | Service status check |
| GET | `/health` | Health check |
| **Users** |
| POST | `/users/` | Create user |
| GET | `/users/` | Get all users |
| PUT/PATCH | `/users/<email>` | Update user |
| **Invites** |
| POST | `/invites/` | Create invite code |
| **Files** |
| POST | `/file/upload` | Upload file |
| GET | `/file/get/<filename>` | Download file |
| GET | `/file/getAll` | List all files |
| **Meetings** |
| POST | `/meetings/` | Create meeting |
| GET | `/meetings/` | Get all meetings |
| GET | `/meetings/<meeting_id>` | Get meeting by ID |
| PUT | `/meetings/<meeting_id>` | Update meeting |
| POST | `/meetings/<meeting_id>/start` | Start meeting |
| POST | `/meetings/<meeting_id>/end` | End meeting |
| POST | `/meetings/<meeting_id>/log` | Append log entry |
| GET | `/meetings/<meeting_id>/log` | Get meeting log |
| DELETE | `/meetings/<meeting_id>` | Delete meeting |
| **Manager Codes** |
| POST | `/manager_codes/becameManagerCode` | Create promotion code |
| POST | `/manager_codes/validateBecameManagerCode` | Validate & use code |
| GET | `/manager_codes/becameManagerCode/<code>` | Get code details |
| GET | `/manager_codes/becameManagerCode` | List all codes |

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://admin:password@localhost:5432/savingdb

# Security
INTERNAL_API_KEY=nexus-internal-secret-key-123
SECRET_KEY=your-secret-key

# File Storage
UPLOAD_FOLDER=./storage/files

# Server
DEBUG=False
```

---

## Support & Contact

For technical support or questions about this API:

- **Service:** SAVING_SERVER
- **Version:** 1.0
- **Port:** 5001
- **Documentation Date:** December 7, 2025

---

## Changelog

### Version 1.0 (December 2025)
- Initial release
- User management endpoints
- Meeting management with logging
- File upload/download
- Manager promotion code system
- Invite code system
- Health check endpoints

---

**End of Documentation**
