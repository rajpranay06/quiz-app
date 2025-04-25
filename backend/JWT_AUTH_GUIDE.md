# JWT Authentication Guide for Quiz App

This guide explains how to use JWT authentication in the Quiz App.

## Overview

JSON Web Tokens (JWT) provide a secure way to transmit information between parties. We use them for authentication in this application. The system consists of:

1. Access tokens (short-lived, typically 1 hour)
2. Refresh tokens (longer-lived, typically 1 day)

## Authentication Endpoints

### User Registration
```
POST /api/auth/register/
```

**Request Body:**
```json
{
    "username": "user123",
    "email": "user123@example.com",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "user123",
        "email": "user123@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  // Access token
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."   // Refresh token
}
```

### User Login
```
POST /api/auth/login/
```

**Request Body:**
```json
{
    "username": "user123",
    "password": "securepassword"
}
```

**Response:** (same as registration)

### Get New Access Token
```
POST /api/token/refresh/
```

**Request Body:**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // Your refresh token
}
```

**Response:**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // New access token
}
```

### Verify Token
```
POST /api/token/verify/
```

**Request Body:**
```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // Your access or refresh token
}
```

**Response:**
- 200 OK if token is valid
- 401 Unauthorized if token is invalid

## Using JWT in API Requests

To authenticate your API requests, include the access token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Example using `curl`:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." http://localhost:8000/api/quizzes/
```

Example using JavaScript Fetch:
```javascript
fetch('http://localhost:8000/api/quizzes/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Token Lifecycle

1. **Obtain tokens**: Register or login to receive access and refresh tokens
2. **Use access token**: Include in all authenticated API requests
3. **Token expiration**: Access tokens expire after 1 hour
4. **Refresh token**: When access token expires, use the refresh token to get a new one
5. **Login again**: If both tokens expire, user must login again

## Security Considerations

- Store tokens securely (HttpOnly cookies in browsers)
- Never store tokens in localStorage due to XSS risks
- Implement token rotation for enhanced security
- Use HTTPS in production to prevent token interception

## Swagger Documentation

You can also test JWT authentication through the Swagger UI at `/swagger/`.

1. Click the "Authorize" button
2. Enter your token in the format: `Bearer your_token_here`
3. Click "Authorize" and close the modal
4. All API requests will now include your JWT token 