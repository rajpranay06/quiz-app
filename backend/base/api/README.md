# Quiz App API Documentation

This document outlines the available API endpoints for the Quiz App.

## About this API

This REST API provides access to the functionalities available in the web application but through a simpler, function-based approach. The API is designed to be easy to use and understand.

## Authentication

All API endpoints require authentication using session-based authentication.

## API Endpoints

### API Routes Overview
```
GET /api
```
Returns a list of all available API routes.

### Quizzes

#### List all quizzes
```
GET /api/quizzes/
```
Returns a list of all available quizzes.

#### Get a specific quiz
```
GET /api/quizzes/{quiz_id}/
```
Returns detailed information about a specific quiz, including all questions and options.

#### Create a new quiz
```
POST /api/quizzes/create/
```
Create a new quiz. The authenticated user will be set as the creator.

**Request Body:**
```json
{
  "title": "Quiz Title",
  "description": "Quiz Description"
}
```

#### Update a quiz
```
PUT /api/quizzes/{quiz_id}/update/
```
Update an existing quiz. Only the creator of the quiz can update it.

**Request Body:**
```json
{
  "title": "Updated Quiz Title",
  "description": "Updated Quiz Description"
}
```

#### Delete a quiz
```
DELETE /api/quizzes/{quiz_id}/delete/
```
Delete a quiz. Only the creator of the quiz can delete it.

#### Get quiz questions
```
GET /api/quizzes/{quiz_id}/questions/
```
Get all questions for a specific quiz.

#### Add a question to a quiz
```
POST /api/quizzes/{quiz_id}/add-question/
```
Add a new question to a quiz. Only the creator of the quiz can add questions.

**Request Body:**
```json
{
  "text": "Question text",
  "options": [
    {
      "text": "Option 1",
      "is_correct": true
    },
    {
      "text": "Option 2",
      "is_correct": false
    }
  ]
}
```

#### Submit a quiz
```
POST /api/quizzes/{quiz_id}/submit/
```
Submit answers for a quiz. 

**Request Body:**
```json
{
  "quiz_id": 1,
  "answers": [
    {
      "1": [2, 3]  // Question ID: [Selected Option IDs]
    },
    {
      "2": [5]
    }
  ]
}
```

**Response:**
```json
{
  "score": 75,
  "correct_answers": 3,
  "total_questions": 4,
  "attempt": 1
}
```

#### Get quiz statistics
```
GET /api/quizzes/{quiz_id}/statistics/
```
Get statistics about a quiz.

**Response:**
```json
{
  "total_attempts": 10,
  "average_score": 75.5,
  "highest_score": 100,
  "lowest_score": 50
}
```

### Questions

#### List all questions
```
GET /api/questions/
```
Get all questions. Use query parameter `quiz_id` to filter by quiz.

#### Get a specific question
```
GET /api/questions/{question_id}/
```
Get details about a specific question, including all options.

#### Update a question
```
PUT /api/questions/{question_id}/update/
```
Update a question. Only the creator of the associated quiz can update it.

**Request Body:**
```json
{
  "text": "Updated question text"
}
```

#### Delete a question
```
DELETE /api/questions/{question_id}/delete/
```
Delete a question. Only the creator of the associated quiz can delete it.

#### Add an option to a question
```
POST /api/questions/{question_id}/add-option/
```
Add a new option to a question. Only the creator of the associated quiz can add options.

**Request Body:**
```json
{
  "text": "Option text",
  "is_correct": true
}
```

### User Stats

#### Get user quiz attempts
```
GET /api/user-stats/
```
Get all quiz attempts for the authenticated user.

#### Get user stats summary
```
GET /api/user-stats/summary/
```
Get a summary of the user's quiz statistics.

**Response:**
```json
{
  "total_quizzes_taken": 5,
  "best_score": 100,
  "average_score": 75.5,
  "average_percentage": 85.2,
  "total_attempts": 10
}
```

### Join Quiz

#### Join a quiz
```
POST /api/join-quiz/
```
Join a quiz using its ID.

**Request Body:**
```json
{
  "code": "1"
}
```

**Response:**
```json
{
  "quiz_id": 1,
  "title": "Quiz Title"
}
```

## Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request
- `403 Forbidden`: Not authorized to perform the action
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error 