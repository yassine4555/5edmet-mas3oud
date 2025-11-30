# Meeting API Documentation

## Base URL
```
http://127.0.0.1:5001/meetings
```

All endpoints require the `X-Internal-Key` header for authentication.

---

## Endpoints

### 1. Create Meeting
**POST** `/meetings/`

Create a new meeting with automatic log file generation.

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Team Standup",
  "object": "Daily sync",
  "description": "Daily team standup meeting",
  "created_by": "manager@example.com",
  "password": "meeting123",
  "invited_employees": ["employee@example.com", "john.doe@company.com"]
}
```

**Response (201):**
```json
{
  "id": 1,
  "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Team Standup",
  "object": "Daily sync",
  "description": "Daily team standup meeting",
  "invitation_link": "http://localhost:7053/room/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "log_path": "./storage/meeting_logs/meeting_a1b2c3d4_20251130_120000.log",
  "invited_employees_list": ["employee@example.com", "john.doe@company.com"],
  "created_by": "manager@example.com",
  "created_at": "2025-11-30T12:00:00+00:00",
  "is_active": true,
  "password": "meeting123"
}
```

---

### 2. Get All Meetings
**GET** `/meetings/`

Retrieve all meetings with optional filters.

**Query Parameters:**
- `user_email` (optional): Filter meetings by creator or invited user
- `is_active` (optional): Filter by active status (true/false)

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
```

**Example:**
```
GET /meetings/?user_email=manager@example.com&is_active=true
```

**Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Team Standup",
      "invitation_link": "http://localhost:7053/room/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "created_by": "manager@example.com",
      "created_at": "2025-11-30T12:00:00+00:00",
      "is_active": true,
      "has_password": true
    }
  ]
}
```

---

### 3. Get Meeting by ID
**GET** `/meetings/<meeting_id>`

Get details of a specific meeting.

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
```

**Response (200):**
```json
{
  "id": 1,
  "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Team Standup",
  "log_path": "./storage/meeting_logs/meeting_a1b2c3d4_20251130_120000.log",
  "invited_employees_list": ["employee@example.com"],
  "created_at": "2025-11-30T12:00:00+00:00"
}
```

---

### 4. Update Meeting
**PUT** `/meetings/<meeting_id>`

Update meeting details.

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Updated Meeting Title",
  "description": "New description",
  "invited_employees": ["new@example.com"],
  "is_active": false
}
```

**Response (200):**
```json
{
  "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Updated Meeting Title",
  "updated_at": "2025-11-30T13:00:00+00:00"
}
```

---

### 5. Start Meeting
**POST** `/meetings/<meeting_id>/start`

Mark meeting as started and log the event.

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
```

**Response (200):**
```json
{
  "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "started_at": "2025-11-30T14:00:00+00:00",
  "is_active": true
}
```

---

### 6. End Meeting
**POST** `/meetings/<meeting_id>/end`

Mark meeting as ended and log the event with duration.

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
```

**Response (200):**
```json
{
  "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "started_at": "2025-11-30T14:00:00+00:00",
  "ended_at": "2025-11-30T15:00:00+00:00",
  "is_active": false
}
```

---

### 7. Append to Meeting Log
**POST** `/meetings/<meeting_id>/log`

Add a log entry to the meeting log file.

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
Content-Type: application/json
```

**Request Body:**
```json
{
  "log_entry": "User John joined the meeting"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Log entry added"
}
```

---

### 8. Get Meeting Log
**GET** `/meetings/<meeting_id>/log`

Retrieve meeting log content or download the log file.

**Query Parameters:**
- `download` (optional): Set to `true` to download the file

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
```

**Example (Get Content):**
```
GET /meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/log
```

**Response (200):**
```json
{
  "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "log_path": "./storage/meeting_logs/meeting_a1b2c3d4_20251130_120000.log",
  "log_content": "Meeting Log: Team Standup\nMeeting ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890\n..."
}
```

**Example (Download):**
```
GET /meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/log?download=true
```

Returns the log file as a download.

---

### 9. Delete Meeting
**DELETE** `/meetings/<meeting_id>`

Soft delete a meeting (marks as inactive).

**Headers:**
```
X-Internal-Key: nexus-internal-secret-key-123
```

**Response (200):**
```json
{
  "success": true,
  "message": "Meeting deleted"
}
```

---

## Log File Format

Meeting log files are automatically created in `./storage/meeting_logs/` with the format:

```
Meeting Log: Team Standup
Meeting ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Created By: manager@example.com
Created At: 2025-11-30 12:00:00
Invitation Link: http://localhost:7053/room/a1b2c3d4-e5f6-7890-abcd-ef1234567890
================================================================================

[2025-11-30 14:00:00] Meeting started
[2025-11-30 14:05:00] User John joined the meeting
[2025-11-30 14:30:00] Screen sharing started
[2025-11-30 15:00:00] Meeting ended
Duration: 1:00:00
```

---

## Usage Examples

### Python Example:
```python
import requests

headers = {
    'X-Internal-Key': 'nexus-internal-secret-key-123',
    'Content-Type': 'application/json'
}

# Create meeting
response = requests.post(
    'http://localhost:5001/meetings/',
    headers=headers,
    json={
        "title": "Team Meeting",
        "created_by": "manager@example.com",
        "invited_employees": ["employee@example.com"]
    }
)
meeting = response.json()
meeting_id = meeting['meeting_id']

# Start meeting
requests.post(f'http://localhost:5001/meetings/{meeting_id}/start', headers=headers)

# Add log entries
requests.post(
    f'http://localhost:5001/meetings/{meeting_id}/log',
    headers=headers,
    json={"log_entry": "User joined"}
)

# End meeting
requests.post(f'http://localhost:5001/meetings/{meeting_id}/end', headers=headers)

# Get log content
log_response = requests.get(f'http://localhost:5001/meetings/{meeting_id}/log', headers=headers)
print(log_response.json()['log_content'])
```

---

## Database Migration

After adding the meeting model, run:

```bash
# Option 1: Re-run the SQL script
psql -U postgres -d savingdb -f create_database.sql

# Option 2: Use Flask-Migrate
flask db migrate -m "Add meetings table"
flask db upgrade
```
