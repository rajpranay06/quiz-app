# Quiz Application

A full-featured quiz platform built with Django REST Framework and JavaScript, allowing users to create, take, and analyze quizzes.

## Features

- **User Authentication**
  - JWT (JSON Web Token) based authentication
  - Register and login functionality
  - Token refresh mechanism
  
- **Quiz Management**
  - Create custom quizzes
  - Add multiple-choice questions with single or multiple correct answers
  - Edit and delete quizzes and questions
  - Track quiz statistics

- **Quiz Taking**
  - Join quizzes via quiz codes
  - Interactive quiz interface
  - Real-time scoring
  - Multiple attempts support

- **Statistics and Analytics**
  - User performance tracking
  - Quiz-specific statistics
  - Visual performance charts

## Tech Stack

- **Backend**
  - Django + Django REST Framework
  - SQLite database
  - REST API with JWT authentication
  - Swagger API documentation

- **Frontend**
  - HTML/CSS/JavaScript
  - Bootstrap for responsive design
  - Chart.js for data visualization

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/quiz-app.git
   cd quiz-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**
   ```bash
   cd backend
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Access the application**
   - Web interface: http://localhost:8000/
   - Admin panel: http://localhost:8000/admin/
   - API documentation: http://localhost:8000/swagger/

## API Usage

The application provides a comprehensive REST API. Please refer to the [JWT Authentication Guide](backend/JWT_AUTH_GUIDE.md) for details on how to authenticate with the API.

### Key Endpoints

- **Authentication**
  - `POST /api/auth/register/` - Register a new user
  - `POST /api/auth/login/` - Login and get tokens
  - `POST /api/token/refresh/` - Refresh access token

- **Quizzes**
  - `GET /api/quizzes/` - List all quizzes
  - `POST /api/quizzes/create/` - Create a new quiz
  - `GET /api/quizzes/{id}/` - Get quiz details
  - `PUT /api/quizzes/{id}/update/` - Update a quiz
  - `DELETE /api/quizzes/{id}/delete/` - Delete a quiz

- **Questions**
  - `GET /api/quizzes/{id}/questions/` - Get quiz questions
  - `POST /api/quizzes/{id}/add-question/` - Add a question to a quiz
  - `PUT /api/questions/{id}/update/` - Update a question
  - `DELETE /api/questions/{id}/delete/` - Delete a question

- **Quiz Taking**
  - `POST /api/join-quiz/` - Join a quiz by code
  - `POST /api/quizzes/{id}/submit/` - Submit quiz answers

- **Statistics**
  - `GET /api/user-stats/` - Get user statistics
  - `GET /api/quizzes/{id}/statistics/` - Get quiz statistics

## Application Structure

```
quiz-app/
├── backend/               # Django backend
│   ├── backend/           # Django project settings
│   └── base/              # Main application
│       ├── api/           # API views, serializers, and URLs
│       ├── models/        # Database models
│       ├── templates/     # HTML templates
│       └── static/        # Static files (CSS, JS, images)
└── frontend/              # Frontend code (if separated)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django and Django REST Framework documentation
- JWT authentication implementation based on djangorestframework-simplejwt


