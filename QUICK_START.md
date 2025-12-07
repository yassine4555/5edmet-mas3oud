# SAVING_SERVER API - Quick Start Guide

## 🚀 Quick Setup

1. **Start the server:**
   ```bash
   cd d:\iset\3eme\S1\integration\projet\work\DataBase\masoud\nexus
   .\venv\Scripts\activate
   python app.py
   ```

2. **Server will run on:** `http://localhost:5001`

3. **API Key:** `nexus-internal-secret-key-123`

---

## 📋 Common Tasks

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

### Update a User
```bash
curl -X PUT http://localhost:5001/users/user@company.com \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"department": "IT"}'
```

### Create a Meeting
```bash
curl -X POST http://localhost:5001/meetings/ \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
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

### Promote Employee to Manager
```bash
# Step 1: HR creates promotion code
curl -X POST http://localhost:5001/manager_codes/becameManagerCode \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "hrid": "hr_user_123",
    "code": "PROMOTE2025"
  }'

# Step 2: Use the code to promote employee
curl -X POST http://localhost:5001/manager_codes/validateBecameManagerCode \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PROMOTE2025",
    "userMail": "employee@company.com"
  }'
```

---

## 📚 Full Documentation

See `COMPLETE_API_DOCUMENTATION.md` for detailed information.

---

## 🔑 Authentication

All requests require the API key header:
```
X-Internal-Key: nexus-internal-secret-key-123
```

---

## 📌 Base Paths

- Users: `/users`
- Meetings: `/meetings`
- Files: `/file`
- Invites: `/invites`
- Manager Codes: `/manager_codes`

---

## 🆘 Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Missing API key | Add `X-Internal-Key` header |
| 404 Not Found | Wrong URL or resource doesn't exist | Check endpoint path |
| 409 Conflict | Duplicate email/code | Use unique values |
| 422 Missing Field | Required field not provided | Check request body |

---

## 🧪 Test the API

Run the test suite:
```bash
python verify_api.py
```
