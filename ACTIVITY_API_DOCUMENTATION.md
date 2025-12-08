# Activity API Documentation - Server Team Guide

## Overview

The Activity API provides full CRUD operations for managing team activities and events. Activities can track meetings, training sessions, team building events, workshops, and other team-related events with participant management.

**Base URL:** `http://localhost:5001/activities`

**Authentication:** All endpoints require the `X-Internal-Key` header.

```bash
X-Internal-Key: nexus-internal-secret-key-123
```

---

## Data Model

### Activity Entity

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Auto | Database primary key |
| `activity_id` | string (UUID) | Auto | Unique identifier for API operations |
| `date` | datetime | Yes | Date and time of the activity |
| `type` | string | Yes | Type of activity |
| `title` | string | No | Activity title |
| `description` | text | No | Detailed description |
| `creator` | string (email) | Yes | Email of the user who created the activity |
| `employees_joined` | array | No | List of participant emails |
| `status` | string | No | Activity status (default: "scheduled") |
| `created_at` | datetime | Auto | Creation timestamp |
| `updated_at` | datetime | Auto | Last update timestamp |

### Valid Activity Types

- `meeting`
- `training`
- `team_building`
- `workshop`
- `presentation`
- `review`
- `other`

### Valid Status Values

- `scheduled` (default)
- `ongoing`
- `completed`
- `cancelled`

---

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/activities/` | Create a new activity |
| GET | `/activities/` | List all activities (with filters) |
| GET | `/activities/<activity_id>` | Get a specific activity |
| PUT/PATCH | `/activities/<activity_id>` | Update an activity |
| DELETE | `/activities/<activity_id>` | Delete an activity |
| POST | `/activities/<activity_id>/join` | Add participant to activity |
| POST | `/activities/<activity_id>/leave` | Remove participant from activity |
| GET | `/activities/<activity_id>/participants` | Get activity participants |
| GET | `/activities/user/<email>` | Get activities for a user |

---

## Endpoint Details

### 1. Create Activity

**POST** `/activities/`

Creates a new activity.

#### Request Body

```json
{
    "date": "2025-12-15T14:00:00",
    "creator": "manager@company.com",
    "type": "training",
    "title": "Python Advanced Training",
    "description": "Advanced Python programming techniques",
    "employees_joined": ["employee1@company.com", "employee2@company.com"],
    "status": "scheduled"
}
```

#### Required Fields

- `date` - ISO format datetime (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD)
- `creator` - Must be an existing user email
- `type` - One of the valid activity types

#### Example Request

```bash
curl -X POST "http://localhost:5001/activities/" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-15T14:00:00",
    "creator": "manager@company.com",
    "type": "training",
    "title": "Python Advanced Training",
    "description": "Advanced Python programming techniques"
  }'
```

#### Success Response (201 Created)

```json
{
    "success": true,
    "message": "Activity created successfully",
    "data": {
        "id": 1,
        "activity_id": "550e8400-e29b-41d4-a716-446655440000",
        "date": "2025-12-15T14:00:00+00:00",
        "type": "training",
        "title": "Python Advanced Training",
        "description": "Advanced Python programming techniques",
        "creator": "manager@company.com",
        "employees_joined": [],
        "status": "scheduled",
        "created_at": "2025-12-07T10:30:00+00:00",
        "updated_at": "2025-12-07T10:30:00+00:00"
    }
}
```

#### Error Responses

- `422` - Missing required field
- `404` - Creator user not found
- `400` - Invalid activity type or date format

---

### 2. List Activities

**GET** `/activities/`

Retrieves all activities with optional filtering.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `creator` | string | Filter by creator email |
| `type` | string | Filter by activity type |
| `status` | string | Filter by status |
| `employee` | string | Filter activities where this employee has joined |
| `from_date` | string | Filter activities from this date (YYYY-MM-DD) |
| `to_date` | string | Filter activities until this date (YYYY-MM-DD) |

#### Example Requests

```bash
# Get all activities
curl -X GET "http://localhost:5001/activities/" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# Get training activities
curl -X GET "http://localhost:5001/activities/?type=training" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# Get scheduled activities by creator
curl -X GET "http://localhost:5001/activities/?creator=manager@company.com&status=scheduled" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# Get activities for a date range
curl -X GET "http://localhost:5001/activities/?from_date=2025-12-01&to_date=2025-12-31" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# Get activities where a specific employee joined
curl -X GET "http://localhost:5001/activities/?employee=alice@company.com" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "count": 2,
    "data": [
        {
            "id": 1,
            "activity_id": "550e8400-e29b-41d4-a716-446655440000",
            "date": "2025-12-15T14:00:00+00:00",
            "type": "training",
            "title": "Python Advanced Training",
            "creator": "manager@company.com",
            "employees_joined": ["alice@company.com", "bob@company.com"],
            "status": "scheduled"
        },
        {
            "id": 2,
            "activity_id": "660e8400-e29b-41d4-a716-446655440001",
            "date": "2025-12-20T10:00:00+00:00",
            "type": "team_building",
            "title": "Holiday Team Event",
            "creator": "hr@company.com",
            "employees_joined": [],
            "status": "scheduled"
        }
    ]
}
```

---

### 3. Get Single Activity

**GET** `/activities/<activity_id>`

Retrieves a specific activity by its `activity_id` (UUID) or numeric `id`.

#### Example Requests

```bash
# By activity_id (UUID)
curl -X GET "http://localhost:5001/activities/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# By numeric id
curl -X GET "http://localhost:5001/activities/1" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "data": {
        "id": 1,
        "activity_id": "550e8400-e29b-41d4-a716-446655440000",
        "date": "2025-12-15T14:00:00+00:00",
        "type": "training",
        "title": "Python Advanced Training",
        "description": "Advanced Python programming techniques",
        "creator": "manager@company.com",
        "employees_joined": ["alice@company.com", "bob@company.com"],
        "status": "scheduled",
        "created_at": "2025-12-07T10:30:00+00:00",
        "updated_at": "2025-12-07T10:30:00+00:00"
    }
}
```

#### Error Response (404 Not Found)

```json
{
    "success": false,
    "error": "Activity not found"
}
```

---

### 4. Update Activity

**PUT/PATCH** `/activities/<activity_id>`

Updates an existing activity.

#### Updatable Fields

- `title`
- `description`
- `type`
- `date`
- `employees_joined`
- `status`

#### Example Request

```bash
curl -X PUT "http://localhost:5001/activities/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Advanced Training - Updated",
    "status": "ongoing",
    "employees_joined": ["alice@company.com", "bob@company.com", "charlie@company.com"]
  }'
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "message": "Activity updated successfully. Updated fields: title, status, employees_joined",
    "data": {
        "id": 1,
        "activity_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Python Advanced Training - Updated",
        "status": "ongoing",
        "employees_joined": ["alice@company.com", "bob@company.com", "charlie@company.com"]
    }
}
```

---

### 5. Delete Activity

**DELETE** `/activities/<activity_id>`

Deletes an activity permanently.

#### Example Request

```bash
curl -X DELETE "http://localhost:5001/activities/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "message": "Activity deleted successfully",
    "deleted_activity": {
        "id": 1,
        "activity_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Python Advanced Training"
    }
}
```

---

### 6. Join Activity

**POST** `/activities/<activity_id>/join`

Adds an employee to an activity's participants list.

#### Request Body

```json
{
    "employee_email": "alice@company.com"
}
```

#### Example Request

```bash
curl -X POST "http://localhost:5001/activities/550e8400-e29b-41d4-a716-446655440000/join" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"employee_email": "alice@company.com"}'
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "message": "Employee alice@company.com joined the activity",
    "data": {
        "activity_id": "550e8400-e29b-41d4-a716-446655440000",
        "employees_joined": ["alice@company.com"]
    }
}
```

#### Error Responses

- `404` - Activity not found or Employee not found
- `409` - Employee is already in this activity
- `422` - Missing employee_email field

---

### 7. Leave Activity

**POST** `/activities/<activity_id>/leave`

Removes an employee from an activity's participants list.

#### Request Body

```json
{
    "employee_email": "alice@company.com"
}
```

#### Example Request

```bash
curl -X POST "http://localhost:5001/activities/550e8400-e29b-41d4-a716-446655440000/leave" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"employee_email": "alice@company.com"}'
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "message": "Employee alice@company.com left the activity",
    "data": {
        "activity_id": "550e8400-e29b-41d4-a716-446655440000",
        "employees_joined": []
    }
}
```

#### Error Response (404)

```json
{
    "success": false,
    "error": "Employee is not in this activity"
}
```

---

### 8. Get Activity Participants

**GET** `/activities/<activity_id>/participants`

Retrieves all participants of an activity with optional detailed user information.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `include_details` | boolean | If true, returns full user objects |

#### Example Requests

```bash
# Basic (email list only)
curl -X GET "http://localhost:5001/activities/550e8400-e29b-41d4-a716-446655440000/participants" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# With full details
curl -X GET "http://localhost:5001/activities/550e8400-e29b-41d4-a716-446655440000/participants?include_details=true" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

#### Success Response (200 OK) - Basic

```json
{
    "success": true,
    "activity_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Python Advanced Training",
    "creator": {
        "email": "manager@company.com",
        "first_name": "John",
        "last_name": "Manager"
    },
    "participants": ["alice@company.com", "bob@company.com"],
    "participants_count": 2
}
```

#### Success Response (200 OK) - With Details

```json
{
    "success": true,
    "activity_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Python Advanced Training",
    "creator": {
        "email": "manager@company.com",
        "first_name": "John",
        "last_name": "Manager"
    },
    "participants": [
        {
            "id": 2,
            "email": "alice@company.com",
            "first_name": "Alice",
            "last_name": "Smith",
            "role": "employee",
            "department": "Engineering"
        },
        {
            "id": 3,
            "email": "bob@company.com",
            "first_name": "Bob",
            "last_name": "Johnson",
            "role": "employee",
            "department": "Engineering"
        }
    ],
    "participants_count": 2
}
```

---

### 9. Get User Activities

**GET** `/activities/user/<email>`

Retrieves all activities for a specific user (activities they created or joined).

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `filter` | string | Filter type: `all` (default), `created`, or `joined` |

#### Example Requests

```bash
# All activities for user
curl -X GET "http://localhost:5001/activities/user/alice@company.com" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# Only activities created by user
curl -X GET "http://localhost:5001/activities/user/alice@company.com?filter=created" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"

# Only activities user has joined
curl -X GET "http://localhost:5001/activities/user/alice@company.com?filter=joined" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "user": "alice@company.com",
    "filter": "all",
    "count": 3,
    "data": [
        {
            "id": 1,
            "activity_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Python Advanced Training",
            "type": "training",
            "creator": "manager@company.com",
            "employees_joined": ["alice@company.com"]
        }
    ]
}
```

---

## Code Examples

### Python

```python
import requests

BASE_URL = "http://localhost:5001/activities"
HEADERS = {
    "X-Internal-Key": "nexus-internal-secret-key-123",
    "Content-Type": "application/json"
}

# Create activity
def create_activity(date, creator, activity_type, title=None, description=None):
    data = {
        "date": date,
        "creator": creator,
        "type": activity_type,
        "title": title,
        "description": description
    }
    response = requests.post(BASE_URL + "/", json=data, headers=HEADERS)
    return response.json()

# Get all activities
def get_activities(filters=None):
    response = requests.get(BASE_URL + "/", params=filters, headers=HEADERS)
    return response.json()

# Join activity
def join_activity(activity_id, employee_email):
    data = {"employee_email": employee_email}
    response = requests.post(f"{BASE_URL}/{activity_id}/join", json=data, headers=HEADERS)
    return response.json()

# Usage
new_activity = create_activity(
    date="2025-12-15T14:00:00",
    creator="manager@company.com",
    activity_type="training",
    title="Python Workshop"
)
print(f"Created: {new_activity['data']['activity_id']}")

# Add participant
join_activity(new_activity['data']['activity_id'], "alice@company.com")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5001/activities';
const HEADERS = {
    'X-Internal-Key': 'nexus-internal-secret-key-123',
    'Content-Type': 'application/json'
};

// Create activity
async function createActivity(date, creator, type, title, description) {
    const response = await axios.post(BASE_URL + '/', {
        date, creator, type, title, description
    }, { headers: HEADERS });
    return response.data;
}

// Get all activities
async function getActivities(filters = {}) {
    const response = await axios.get(BASE_URL + '/', {
        headers: HEADERS,
        params: filters
    });
    return response.data;
}

// Join activity
async function joinActivity(activityId, employeeEmail) {
    const response = await axios.post(`${BASE_URL}/${activityId}/join`, {
        employee_email: employeeEmail
    }, { headers: HEADERS });
    return response.data;
}

// Usage
(async () => {
    const activity = await createActivity(
        '2025-12-15T14:00:00',
        'manager@company.com',
        'training',
        'Python Workshop'
    );
    console.log('Created:', activity.data.activity_id);
    
    await joinActivity(activity.data.activity_id, 'alice@company.com');
})();
```

---

## Error Handling

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid type, status, or date format |
| 401 | Unauthorized | Missing or invalid X-Internal-Key |
| 404 | Not Found | Activity or user doesn't exist |
| 409 | Conflict | Employee already in activity |
| 422 | Unprocessable Entity | Missing required field |
| 500 | Server Error | Database or server issues |

### Error Response Format

```json
{
    "success": false,
    "error": "Error message description"
}
```

---

## Database Setup

### Running Migration

If Flask-Migrate works:

```bash
flask db migrate -m "Add activities table"
flask db upgrade
```

If manual migration needed, run the SQL script:

```bash
psql -U your_user -d your_database -f migrations/add_activities_table.sql
```

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────────┐
│                    ACTIVITY API QUICK REFERENCE                │
├────────────────────────────────────────────────────────────────┤
│ CREATE       POST   /activities/                               │
│ LIST         GET    /activities/?type=training&status=scheduled│
│ GET ONE      GET    /activities/<activity_id>                  │
│ UPDATE       PUT    /activities/<activity_id>                  │
│ DELETE       DELETE /activities/<activity_id>                  │
│ JOIN         POST   /activities/<activity_id>/join             │
│ LEAVE        POST   /activities/<activity_id>/leave            │
│ PARTICIPANTS GET    /activities/<activity_id>/participants     │
│ USER ACTS    GET    /activities/user/<email>                   │
├────────────────────────────────────────────────────────────────┤
│ HEADER: X-Internal-Key: nexus-internal-secret-key-123          │
│ TYPES: meeting, training, team_building, workshop,             │
│        presentation, review, other                             │
│ STATUS: scheduled, ongoing, completed, cancelled               │
└────────────────────────────────────────────────────────────────┘
```

---

## Support

For questions or issues:
- Check main documentation: `COMPLETE_API_DOCUMENTATION.md`
- Review error messages in responses
- Enable debug logging

---

**API Version:** 1.0  
**Last Updated:** December 7, 2025  
**Base URL:** `http://localhost:5001/activities`
