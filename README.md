# Mind Clash - Quiz Application

Mind clash is a web based quiz application, where users can create, play and manage quizzes.  

## Application Features

✅ User Registration & Authentication  
✅ Token-based Authentication (DRF Tokens)  
✅ Create & Play Quizzes    
✅ User Stats Dashboard  
✅ CI Integration with CircleCI  
✅ Dockerized Deployment  

## 🛠️ **API Endpoints**

### **Authentication**

| Method |   Endpoint   |         Description             |
|--------|--------------|---------------------------------|
| `POST` | `/register/` | User registration               |
| `POST` | `/login/`    | User login (returns auth token) |
| `POST` | `/logout/`   | User logout (deletes token)     | 

### **Quiz Management**

|  Method  |         Endpoint            |         Description             |
|----------|-----------------------------|---------------------------------|
| `POST`   | `/create-quiz/`             | Create a new quiz               |
| `POST`   | `/add_questions/<quiz_id>/` | Add questions to a quiz         |
| `GET`    | `/play_quiz/<quiz_id>/`     | Play a quiz                     |
| `POST`   | `/submit_quiz/<quiz_id>/`   | Submit quiz and calculate score |
| `PUT`    | `/update_quiz/<quiz_id>/`   | Update an existing quiz         |
| `DELETE` | `/delete_quiz/<quiz_id>/`   | Delete a quiz                   |



# Implementation Details

## User Authentication

Implemented Django authentication for user registration and login. Integrated Token Authentication using Django Rest Framework (DRF). Users receive a token upon login, which is required for API authentication.

# Quiz Creation

Users can create quizzes via an API (/create-quiz/).

Each quiz has a title, description, and creator (user) stored in the Quiz model.

# Adding Questions

Users can add questions via an API (/add-questions/<quiz_id>/).

Each question has 4 options, and one option is marked as correct. Used the Question model to store quiz-related questions.

# Playing a Quiz
Users can select a quiz and answer questions (/play_quiz/<quiz_id>/). Implemented form-based UI for answering questions.

The backend evaluates the answers and calculates scores.

# Updating & Deleting Quizzes
Users can edit quizzes they created (/update-quiz/<quiz_id>/).

Added a feature to delete individual questions or the entire quiz (/delete-quiz/<quiz_id>/).

# Security Features
Implemented Token Authentication for secure API access. CORS protection to allow frontend-backend communication.

Permissions enforced so only quiz creators can edit or delete their quizzes.

# Technologies Used
✅ Django & Django REST Framework (Backend)
✅ SQLite (Database)
✅ Docker (Containerization)
✅ CircleCI (Continuous Integration)
✅ Swagger (API Documentation)


