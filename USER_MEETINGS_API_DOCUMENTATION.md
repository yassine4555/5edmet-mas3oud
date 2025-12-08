# User Meetings API Documentation

## Overview

This document describes the API endpoints for managing user meetings in the SAVING_SERVER system. These endpoints allow users to:

1. **Get all meetings** related to a specific user (created or invited)
2. **Get upcoming meetings** for a user
3. **Delete meetings** (only by the creator)

---

## Authentication

All endpoints require the `X-Internal-Key` header:

```
X-Internal-Key: nexus-internal-secret-key-123
```

---

## Endpoints

### 1. Get User Meetings

**Endpoint:** `GET /meetings/user/<email>`

**Description:** Get all meetings related to a specific user - both meetings they created and meetings they've been invited to.

#### Request

```bash
GET /meetings/user/ahmed.manager@test.com
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter` | string | `all` | Filter type: `all`, `created`, `invited` |
| `is_active` | boolean | - | Filter by active status: `true` or `false` |
| `include_details` | boolean | `false` | Include creator user details |

#### Example Requests

**Get all meetings for a user:**
```bash
curl -X GET "http://localhost:5001/meetings/user/ahmed.manager@test.com" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

**Get only meetings created by user:**
```bash
curl -X GET "http://localhost:5001/meetings/user/ahmed.manager@test.com?filter=created" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

**Get only meetings user was invited to:**
```bash
curl -X GET "http://localhost:5001/meetings/user/ahmed.manager@test.com?filter=invited" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

**Get active meetings with creator details:**
```bash
curl -X GET "http://localhost:5001/meetings/user/ahmed.manager@test.com?is_active=true&include_details=true" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "user": "ahmed.manager@test.com",
  "filter": "all",
  "statistics": {
    "total": 5,
    "created": 3,
    "invited": 2
  },
  "data": [
    {
      "id": 1,
      "meeting_id": "abc-123-xyz",
      "title": "Team Standup",
      "object": "Daily sync",
      "description": "Morning standup meeting",
      "created_by": "ahmed.manager@test.com",
      "invited_employees_list": ["employee1@test.com", "employee2@test.com"],
      "is_active": true,
      "started_at": null,
      "ended_at": null,
      "created_at": "2025-12-08T10:00:00Z",
      "relationship": "creator"
    },
    {
      "id": 2,
      "meeting_id": "def-456-uvw",
      "title": "Project Review",
      "object": "Q4 Review",
      "description": "Quarterly project review",
      "created_by": "manager@test.com",
      "invited_employees_list": ["ahmed.manager@test.com", "employee1@test.com"],
      "is_active": true,
      "started_at": null,
      "ended_at": null,
      "created_at": "2025-12-07T14:00:00Z",
      "relationship": "invited",
      "creator_details": {
        "email": "manager@test.com",
        "first_name": "John",
        "last_name": "Manager",
        "department": "Engineering"
      }
    }
  ]
}
```

#### Error Responses

**User Not Found (404):**
```json
{
  "success": false,
  "error": "User not found"
}
```

---

### 2. Get User Upcoming Meetings

**Endpoint:** `GET /meetings/user/<email>/upcoming`

**Description:** Get all upcoming (active) meetings for a user, separated by status (not started vs in progress).

#### Request

```bash
GET /meetings/user/ahmed.manager@test.com/upcoming
```

#### Example Request

```bash
curl -X GET "http://localhost:5001/meetings/user/ahmed.manager@test.com/upcoming" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "user": "ahmed.manager@test.com",
  "upcoming": {
    "not_started": [
      {
        "id": 1,
        "meeting_id": "abc-123-xyz",
        "title": "Team Standup",
        "created_by": "ahmed.manager@test.com",
        "is_active": true,
        "started_at": null,
        "ended_at": null
      }
    ],
    "in_progress": [
      {
        "id": 3,
        "meeting_id": "ghi-789-rst",
        "title": "Sprint Planning",
        "created_by": "ahmed.manager@test.com",
        "is_active": true,
        "started_at": "2025-12-08T09:00:00Z",
        "ended_at": null
      }
    ]
  },
  "counts": {
    "not_started": 1,
    "in_progress": 1,
    "total": 2
  }
}
```

---

### 3. Delete Meeting (Soft Delete)

**Endpoint:** `DELETE /meetings/<meeting_id>`

**Description:** Soft delete a meeting by marking it as inactive. **Only the creator of the meeting can delete it.**

#### Request Body

```json
{
  "user_email": "creator@example.com"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_email` | string | Yes | Email of the user requesting deletion (must be creator) |

#### Example Request

```bash
curl -X DELETE "http://localhost:5001/meetings/abc-123-xyz" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "ahmed.manager@test.com"
  }'
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Meeting deleted successfully",
  "meeting_id": "abc-123-xyz",
  "deleted_by": "ahmed.manager@test.com"
}
```

#### Error Responses

**Meeting Not Found (404):**
```json
{
  "success": false,
  "error": "Meeting not found"
}
```

**Missing user_email (422):**
```json
{
  "success": false,
  "error": "user_email is required to delete a meeting"
}
```

**Not the Creator (403):**
```json
{
  "success": false,
  "error": "Only the creator of the meeting can delete it",
  "created_by": "original.creator@test.com",
  "requested_by": "other.user@test.com"
}
```

---

### 4. Hard Delete Meeting (Permanent)

**Endpoint:** `DELETE /meetings/<meeting_id>/hard-delete`

**Description:** Permanently delete a meeting from the database. **Only the creator can do this. This action is irreversible.**

#### Request Body

```json
{
  "user_email": "creator@example.com",
  "confirm": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_email` | string | Yes | Email of the user requesting deletion (must be creator) |
| `confirm` | boolean | Yes | Must be `true` to confirm permanent deletion |

#### Example Request

```bash
curl -X DELETE "http://localhost:5001/meetings/abc-123-xyz/hard-delete" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "ahmed.manager@test.com",
    "confirm": true
  }'
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Meeting permanently deleted",
  "meeting_id": "abc-123-xyz",
  "title": "Team Standup",
  "deleted_by": "ahmed.manager@test.com"
}
```

#### Error Responses

**Missing Confirmation (422):**
```json
{
  "success": false,
  "error": "Please set 'confirm': true to permanently delete this meeting"
}
```

---

## Code Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:5001"
HEADERS = {
    "X-Internal-Key": "nexus-internal-secret-key-123",
    "Content-Type": "application/json"
}

# Get all meetings for a user
def get_user_meetings(email, filter_type='all', is_active=None, include_details=False):
    params = {'filter': filter_type}
    if is_active is not None:
        params['is_active'] = str(is_active).lower()
    if include_details:
        params['include_details'] = 'true'
    
    response = requests.get(
        f"{BASE_URL}/meetings/user/{email}",
        headers=HEADERS,
        params=params
    )
    return response.json()

# Get upcoming meetings
def get_upcoming_meetings(email):
    response = requests.get(
        f"{BASE_URL}/meetings/user/{email}/upcoming",
        headers=HEADERS
    )
    return response.json()

# Delete a meeting (soft delete)
def delete_meeting(meeting_id, user_email):
    response = requests.delete(
        f"{BASE_URL}/meetings/{meeting_id}",
        headers=HEADERS,
        json={"user_email": user_email}
    )
    return response.json()

# Permanently delete a meeting
def hard_delete_meeting(meeting_id, user_email):
    response = requests.delete(
        f"{BASE_URL}/meetings/{meeting_id}/hard-delete",
        headers=HEADERS,
        json={
            "user_email": user_email,
            "confirm": True
        }
    )
    return response.json()

# Usage examples
if __name__ == "__main__":
    email = "ahmed.manager@test.com"
    
    # Get all meetings
    print("All meetings:")
    result = get_user_meetings(email)
    print(f"Total: {result['statistics']['total']}")
    print(f"Created: {result['statistics']['created']}")
    print(f"Invited: {result['statistics']['invited']}")
    
    # Get only created meetings
    print("\nCreated meetings:")
    result = get_user_meetings(email, filter_type='created')
    for meeting in result['data']:
        print(f"  - {meeting['title']}")
    
    # Get upcoming meetings
    print("\nUpcoming meetings:")
    result = get_upcoming_meetings(email)
    print(f"Not started: {result['counts']['not_started']}")
    print(f"In progress: {result['counts']['in_progress']}")
    
    # Delete a meeting (only if you're the creator)
    meeting_id = "abc-123-xyz"
    result = delete_meeting(meeting_id, email)
    if result['success']:
        print(f"\nMeeting {meeting_id} deleted successfully")
    else:
        print(f"\nFailed to delete: {result['error']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5001';
const HEADERS = {
  'X-Internal-Key': 'nexus-internal-secret-key-123',
  'Content-Type': 'application/json'
};

// Get all meetings for a user
async function getUserMeetings(email, options = {}) {
  const params = new URLSearchParams();
  params.append('filter', options.filter || 'all');
  if (options.isActive !== undefined) {
    params.append('is_active', options.isActive.toString());
  }
  if (options.includeDetails) {
    params.append('include_details', 'true');
  }

  const response = await axios.get(
    `${BASE_URL}/meetings/user/${email}?${params}`,
    { headers: HEADERS }
  );
  return response.data;
}

// Get upcoming meetings
async function getUpcomingMeetings(email) {
  const response = await axios.get(
    `${BASE_URL}/meetings/user/${email}/upcoming`,
    { headers: HEADERS }
  );
  return response.data;
}

// Delete a meeting (soft delete)
async function deleteMeeting(meetingId, userEmail) {
  try {
    const response = await axios.delete(
      `${BASE_URL}/meetings/${meetingId}`,
      {
        headers: HEADERS,
        data: { user_email: userEmail }
      }
    );
    return response.data;
  } catch (error) {
    return error.response.data;
  }
}

// Hard delete a meeting
async function hardDeleteMeeting(meetingId, userEmail) {
  try {
    const response = await axios.delete(
      `${BASE_URL}/meetings/${meetingId}/hard-delete`,
      {
        headers: HEADERS,
        data: {
          user_email: userEmail,
          confirm: true
        }
      }
    );
    return response.data;
  } catch (error) {
    return error.response.data;
  }
}

// Usage
(async () => {
  const email = 'ahmed.manager@test.com';

  // Get all meetings
  const allMeetings = await getUserMeetings(email);
  console.log('Statistics:', allMeetings.statistics);

  // Get created meetings only
  const createdMeetings = await getUserMeetings(email, { filter: 'created' });
  console.log('Created meetings:', createdMeetings.data.length);

  // Get upcoming meetings
  const upcoming = await getUpcomingMeetings(email);
  console.log('Upcoming:', upcoming.counts);

  // Delete a meeting
  const deleteResult = await deleteMeeting('meeting-id-here', email);
  console.log('Delete result:', deleteResult);
})();
```

### React Hook Example

```javascript
import { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://localhost:5001';
const API_KEY = 'nexus-internal-secret-key-123';

export function useUserMeetings(userEmail) {
  const [meetings, setMeetings] = useState([]);
  const [statistics, setStatistics] = useState({ total: 0, created: 0, invited: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMeetings = useCallback(async (filter = 'all') => {
    if (!userEmail) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE}/meetings/user/${userEmail}?filter=${filter}&include_details=true`,
        {
          headers: {
            'X-Internal-Key': API_KEY
          }
        }
      );

      const data = await response.json();

      if (data.success) {
        setMeetings(data.data);
        setStatistics(data.statistics);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userEmail]);

  const deleteMeeting = useCallback(async (meetingId) => {
    try {
      const response = await fetch(`${API_BASE}/meetings/${meetingId}`, {
        method: 'DELETE',
        headers: {
          'X-Internal-Key': API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_email: userEmail })
      });

      const data = await response.json();

      if (data.success) {
        // Remove from local state
        setMeetings(prev => prev.filter(m => m.meeting_id !== meetingId));
        return { success: true };
      } else {
        return { success: false, error: data.error };
      }
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, [userEmail]);

  useEffect(() => {
    fetchMeetings();
  }, [fetchMeetings]);

  return {
    meetings,
    statistics,
    loading,
    error,
    fetchMeetings,
    deleteMeeting
  };
}

// Usage in component
function MeetingsPage({ userEmail }) {
  const { 
    meetings, 
    statistics, 
    loading, 
    error, 
    fetchMeetings,
    deleteMeeting 
  } = useUserMeetings(userEmail);

  const handleDelete = async (meetingId) => {
    if (confirm('Are you sure you want to delete this meeting?')) {
      const result = await deleteMeeting(meetingId);
      if (!result.success) {
        alert(`Failed to delete: ${result.error}`);
      }
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Your Meetings</h2>
      <div>
        <span>Total: {statistics.total}</span>
        <span>Created: {statistics.created}</span>
        <span>Invited: {statistics.invited}</span>
      </div>
      
      <div>
        <button onClick={() => fetchMeetings('all')}>All</button>
        <button onClick={() => fetchMeetings('created')}>Created</button>
        <button onClick={() => fetchMeetings('invited')}>Invited</button>
      </div>

      <ul>
        {meetings.map(meeting => (
          <li key={meeting.meeting_id}>
            <span>{meeting.title}</span>
            <span>({meeting.relationship})</span>
            {meeting.relationship === 'creator' && (
              <button onClick={() => handleDelete(meeting.meeting_id)}>
                Delete
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/meetings/user/<email>` | GET | Get all user meetings |
| `/meetings/user/<email>/upcoming` | GET | Get upcoming meetings |
| `/meetings/<meeting_id>` | DELETE | Soft delete (creator only) |
| `/meetings/<meeting_id>/hard-delete` | DELETE | Permanent delete (creator only) |

---

## Important Notes

1. **Authentication**: All endpoints require the `X-Internal-Key` header
2. **Creator-Only Deletion**: Only the user who created a meeting can delete it
3. **Soft vs Hard Delete**: 
   - Soft delete marks meeting as `is_active = false`
   - Hard delete permanently removes from database
4. **Relationship Field**: Response includes `relationship` field (`creator` or `invited`)
5. **Statistics**: Get endpoint includes counts for total, created, and invited meetings

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized - Missing or invalid API key |
| 403 | Forbidden - User is not the creator |
| 404 | Meeting or user not found |
| 422 | Validation error - Missing required fields |
| 500 | Server error |