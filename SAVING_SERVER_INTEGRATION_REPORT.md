# API Integration Report: Manager Code System

## Overview
The User Service requires integration with the Saving Server to implement a manager promotion code system.

## Required Endpoints in Saving Server

### 1. Save Manager Promotion Code
**Endpoint:** `POST /becameManagerCode`

**Purpose:** Store a code that allows HR to promote employees to managers

**Request Body:**
```json
{
  "hrid": "string",
  "code": "string",
  "max_uses": 1
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Code saved successfully"
}
```

---

### 2. Validate and Use Manager Promotion Code
**Endpoint:** `POST /validateBecameManagerCode`

**Purpose:** Validate code and mark it as used when employee is promoted

**Request Body:**
```json
{
  "code": "string",
  "userMail": "string"
}
```

**Expected Response:**
```json
{
  "valid": true,
  "hrid": "string"
}
```

**Error Response:**
```json
{
  "valid": false,
  "error": "Code invalid/expired/already used"
}
```

---

## User Service Endpoints Using This System

### 1. `/generateBecameManagerCode` (GET)
- Generates random code
- Saves to Saving Server with HR ID
- Returns code to HR user

### 2. `/becameManger` (POST)
- Receives code and user email
- Validates code with Saving Server
- Promotes employee to manager role

---

## Notes
- Codes should have single use (`max_uses: 1`)
- Codes should be stored with HR ID for audit trail
- Consider adding expiration time for codes
- Need error handling for duplicate codes
