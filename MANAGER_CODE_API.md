# Manager Code API Documentation

## Overview
The Manager Code system allows HR users to generate promotion codes that can be used to promote employees to manager role.

## Base URL
All endpoints are relative to the base URL of the SAVING_SERVER (typically `http://localhost:5001`)

## Authentication
All endpoints require an API key to be sent in the `X-API-Key` header.

---

## Endpoints

### 1. Save Manager Promotion Code

**Endpoint:** `POST /becameManagerCode`

**Description:** Store a code that allows HR to promote employees to managers.

**Request Headers:**
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "hrid": "string",           // Required: HR user ID who created the code
  "code": "string",           // Required: The promotion code
  "max_uses": 1               // Optional: Maximum number of uses (default: 1)
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Code saved successfully",
  "data": {
    "id": 1,
    "code": "PROMOTE123",
    "hrid": "hr-user-123",
    "max_uses": 1,
    "used_count": 0,
    "used_by_email": null,
    "is_active": true,
    "created_at": "2025-12-06T10:30:00Z",
    "used_at": null
  }
}
```

**Error Responses:**

*422 Unprocessable Entity* - Missing required fields:
```json
{
  "success": false,
  "error": "Missing required field: hrid"
}
```

*409 Conflict* - Code already exists:
```json
{
  "success": false,
  "error": "Code already exists"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5001/becameManagerCode \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "hrid": "hr-user-123",
    "code": "PROMOTE123",
    "max_uses": 1
  }'
```

---

### 2. Validate and Use Manager Promotion Code

**Endpoint:** `POST /validateBecameManagerCode`

**Description:** Validate code and mark it as used when employee is promoted to manager.

**Request Headers:**
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "code": "string",        // Required: The promotion code
  "userMail": "string"     // Required: Email of user to promote
}
```

**Success Response (200 OK):**
```json
{
  "valid": true,
  "hrid": "hr-user-123",
  "message": "User promoted to manager successfully",
  "user": {
    "id": 5,
    "email": "employee@example.com",
    "userID": "emp-123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "manager",        // Role has been changed to manager
    "department": "Engineering",
    "address": null,
    "date_of_birth": null,
    "employeesList": [],
    "created_at": "2025-12-05T08:00:00Z"
  }
}
```

**Error Responses:**

*422 Unprocessable Entity* - Missing required fields:
```json
{
  "valid": false,
  "error": "Missing required field: code"
}
```

*404 Not Found* - Code or user not found:
```json
{
  "valid": false,
  "error": "Code not found"
}
```

*400 Bad Request* - Invalid code:
```json
{
  "valid": false,
  "error": "Code already used"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5001/validateBecameManagerCode \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PROMOTE123",
    "userMail": "employee@example.com"
  }'
```

---

### 3. Get Manager Code Details

**Endpoint:** `GET /becameManagerCode/<code>`

**Description:** Retrieve information about a specific manager promotion code.

**Request Headers:**
```
X-API-Key: your-api-key
```

**URL Parameters:**
- `code` (string): The promotion code to look up

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "code": "PROMOTE123",
    "hrid": "hr-user-123",
    "max_uses": 1,
    "used_count": 1,
    "used_by_email": "employee@example.com",
    "is_active": false,
    "created_at": "2025-12-06T10:30:00Z",
    "used_at": "2025-12-06T11:45:00Z"
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Code not found"
}
```

**Example cURL:**
```bash
curl -X GET http://localhost:5001/becameManagerCode/PROMOTE123 \
  -H "X-API-Key: your-api-key"
```

---

### 4. List Manager Codes

**Endpoint:** `GET /becameManagerCode`

**Description:** List all manager promotion codes with optional filtering.

**Request Headers:**
```
X-API-Key: your-api-key
```

**Query Parameters:**
- `hrid` (optional): Filter by HR user ID
- `active_only` (optional): Show only active codes (default: false)

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code": "PROMOTE123",
      "hrid": "hr-user-123",
      "max_uses": 1,
      "used_count": 1,
      "used_by_email": "employee@example.com",
      "is_active": false,
      "created_at": "2025-12-06T10:30:00Z",
      "used_at": "2025-12-06T11:45:00Z"
    },
    {
      "id": 2,
      "code": "PROMOTE456",
      "hrid": "hr-user-123",
      "max_uses": 1,
      "used_count": 0,
      "used_by_email": null,
      "is_active": true,
      "created_at": "2025-12-06T12:00:00Z",
      "used_at": null
    }
  ]
}
```

**Example cURL:**
```bash
# Get all codes
curl -X GET http://localhost:5001/becameManagerCode \
  -H "X-API-Key: your-api-key"

# Get codes by specific HR user
curl -X GET "http://localhost:5001/becameManagerCode?hrid=hr-user-123" \
  -H "X-API-Key: your-api-key"

# Get only active codes
curl -X GET "http://localhost:5001/becameManagerCode?active_only=true" \
  -H "X-API-Key: your-api-key"
```

---

## Workflow Example

### Complete promotion flow:

1. **HR generates a code:**
```bash
POST /becameManagerCode
{
  "hrid": "hr-user-123",
  "code": "PROMO2025",
  "max_uses": 1
}
```

2. **HR shares the code with the employee**

3. **Employee uses the code to become a manager:**
```bash
POST /validateBecameManagerCode
{
  "code": "PROMO2025",
  "userMail": "employee@company.com"
}
```

4. **System response includes:**
   - Code is validated
   - Code is marked as used
   - User role is updated to "manager"
   - User data is returned with new role

---

## Business Rules

1. **Single Use**: Codes are designed for single use by default (`max_uses: 1`)
2. **Audit Trail**: All codes store the HR ID who created them
3. **Usage Tracking**: System tracks who used the code and when
4. **Auto-Deactivation**: Codes are automatically deactivated when max uses is reached
5. **User Validation**: User must exist in the system before promotion
6. **Idempotency**: Once a code is used, it cannot be reused

---

## Error Handling

All endpoints follow standard HTTP status codes:
- `200 OK`: Successful GET request
- `201 Created`: Successful POST creation
- `400 Bad Request`: Invalid code state
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate code
- `422 Unprocessable Entity`: Missing required fields
- `500 Internal Server Error`: Server error

---

## Database Schema

```sql
CREATE TABLE manager_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    hrid VARCHAR(255) NOT NULL,
    max_uses INTEGER NOT NULL DEFAULT 1,
    used_count INTEGER NOT NULL DEFAULT 0,
    used_by_email VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE
);
```

---

## Notes

- Consider adding expiration time for codes in future versions
- All timestamps are in UTC
- API key authentication is required for all endpoints
- The system automatically promotes users from any role to "manager"
