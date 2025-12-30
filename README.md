# Issue Tracker API

A production-grade REST API for issue tracking built with FastAPI, PostgreSQL, and SQLAlchemy.

## 🚀 Project Overview

The Issue Tracker API provides a comprehensive backend system for managing software issues, bugs, and feature requests. It implements REST best practices with clean architecture, strong validation, and enterprise-grade features including optimistic concurrency control, bulk operations, and detailed reporting.

## 🛠 Tech Stack

- **Backend Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Migrations**: Alembic for schema management
- **Validation**: Pydantic 2.5 for request/response validation
- **Authentication**: bcrypt for password hashing (ready for JWT integration)
- **Testing**: pytest with async support
- **Documentation**: Auto-generated OpenAPI/Swagger specs

## 📋 Features

- **Issue Management**: Full CRUD operations with workflow states
- **User Management**: Role-based access control (Admin, Manager, Developer, Reporter)
- **Project Organization**: Group issues by projects with ownership
- **Comments System**: Threaded discussions on issues
- **Label System**: Flexible categorization with many-to-many relationships
- **File Attachments**: Secure file upload and management
- **Bulk Operations**: Transactional bulk updates with rollback
- **CSV Import**: Batch issue creation with validation
- **Advanced Reporting**: Performance metrics and analytics
- **Timeline Tracking**: Complete issue history and activity logs
- **Optimistic Locking**: Version-based concurrency control

## 🏗 Architecture

```
app/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and session management
├── models/              # SQLAlchemy models
│   ├── base.py          # Base model with common fields
│   ├── user.py          # User model with roles
│   ├── project.py       # Project model
│   ├── issue.py         # Issue model with workflow
│   ├── comment.py       # Comment model
│   ├── label.py         # Label model
│   ├── issue_label.py   # Many-to-many association
│   └── attachment.py    # File attachment model
├── schemas/             # Pydantic validation schemas
│   ├── common.py        # Shared schemas (pagination, errors)
│   ├── user.py          # User schemas
│   ├── project.py       # Project schemas
│   ├── issue.py         # Issue schemas
│   ├── comment.py       # Comment schemas
│   ├── label.py         # Label schemas
│   └── ...              # Additional schemas
├── routers/             # FastAPI route handlers
│   ├── issues.py        # Issue endpoints
│   ├── users.py         # User endpoints
│   ├── projects.py      # Project endpoints
│   ├── comments.py      # Comment endpoints
│   ├── labels.py         # Label endpoints
│   └── reports.py       # Reporting endpoints
└── services/            # Business logic layer
    ├── base_service.py  # Base service with common functionality
    ├── issue_service.py # Issue business logic
    ├── user_service.py  # User business logic
    └── ...              # Additional services
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip or poetry

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd issue-tracker-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

5. **Set up database**
   ```bash
   # Create database
   createdb issue_tracker
   
   # Run migrations
   alembic upgrade head
   ```

6. **Start the API**
   ```bash
   # Development server
   python run_dev.py
   
   # Or with uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🗄 Database Setup

### Running Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Database Schema

The API uses the following main tables:
- `users` - User accounts with roles
- `projects` - Project containers
- `issues` - Individual issues with workflow states
- `comments` - Issue discussions
- `labels` - Issue categorization
- `issue_labels` - Many-to-many relationship
- `attachments` - File uploads

## 🌐 API Documentation

Once running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📝 Example Requests

### Create an Issue
```bash
curl -X POST "http://localhost:8000/api/v1/issues/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix login bug",
    "description": "Users cannot login with valid credentials",
    "project_id": "uuid-here",
    "creator_id": "uuid-here",
    "priority": "high"
  }'
```

### List Issues with Filters
```bash
curl "http://localhost:8000/api/v1/issues/?status=open&assignee_id=uuid-here&page=1&size=20"
```

### Bulk Status Update
```bash
curl -X POST "http://localhost:8000/api/v1/issues/bulk-status" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_ids": ["uuid-1", "uuid-2"],
    "new_status": "in_progress"
  }'
```

### CSV Import
```bash
curl -X POST "http://localhost:8000/api/v1/issues/import" \
  -F "file=@issues.csv" \
  -F "creator_id=uuid-here"
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_advanced_features.py

# Run with verbose output
pytest -v
```

### Key Test Coverage

- **Optimistic Locking**: Version conflict detection
- **Bulk Operations**: Transactional updates with rollback
- **CSV Import**: Validation and error handling
- **Timeline Generation**: Activity history reconstruction

## 🎯 Design Decisions

### Architecture Patterns

- **Clean Architecture**: Separation of concerns with distinct layers
- **Repository Pattern**: Service layer abstracts database operations
- **Dependency Injection**: FastAPI's dependency system for testability
- **Transaction Management**: Explicit transaction boundaries for data consistency

### Database Design

- **UUID Primary Keys**: Distributed system compatibility and security
- **Soft Delete**: Data preservation with `is_deleted` flags
- **Optimistic Concurrency**: Version fields prevent lost updates
- **Audit Trails**: Automatic timestamp tracking for all entities
- **Proper Indexing**: Performance optimization for common queries

### API Design

- **RESTful Conventions**: Standard HTTP methods and status codes
- **Pagination**: Consistent pagination across all list endpoints
- **Error Handling**: Structured error responses with proper HTTP status codes
- **Validation**: Comprehensive input validation with detailed error messages
- **Documentation**: Auto-generated OpenAPI specifications

### Security Considerations

- **Password Hashing**: bcrypt for secure credential storage
- **Input Validation**: Protection against injection attacks
- **File Upload Security**: Type and size validation for attachments
- **Role-Based Access**: Permission system ready for implementation

## 🔧 Development

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Environment Variables

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/issue_tracker
DEBUG=false
UPLOAD_DIR=uploads
SECRET_KEY=your-secret-key-here
```

## 📊 Reporting Endpoints

### Top Assignees
```bash
curl "http://localhost:8000/api/v1/reports/top-assignees?limit=10"
```

### Resolution Latency
```bash
curl "http://localhost:8000/api/v1/reports/latency?days=30"
```

### Issue Velocity
```bash
curl "http://localhost:8000/api/v1/reports/velocity?days=30"
```

## 🕒 Timeline Feature

Get complete issue history:
```bash
curl "http://localhost:8000/api/v1/issues/{issue_id}/timeline"
```

Returns chronological events including:
- Issue creation
- Status changes
- Comments
- Assignments

## 🚀 Production Considerations

### Performance

- **Connection Pooling**: Optimized database connection management
- **Query Optimization**: Proper indexing and efficient queries
- **Caching**: Ready for Redis integration
- **Async Operations**: FastAPI's async support for scalability

### Monitoring

- **Health Checks**: `/health` endpoint for load balancers
- **Logging**: Structured logging for monitoring
- **Metrics**: Ready for Prometheus integration
- **Error Tracking**: Comprehensive error handling

### Security

- **HTTPS**: Required in production
- **CORS**: Configurable for frontend integration
- **Rate Limiting**: Ready for implementation
- **Authentication**: JWT structure ready for implementation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions and support:
- Create an issue in the repository
- Check the API documentation at `/api/docs`
- Review the test files for usage examples
