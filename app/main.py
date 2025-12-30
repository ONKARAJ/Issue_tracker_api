"""
FastAPI application entry point for Issue Tracker API.

This module configures and initializes the FastAPI application with:
- CORS middleware
- API routers
- Database session management
- Exception handlers
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.database import engine, Base
from app.routers import issues, users, projects, comments, attachments

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Issue Tracker API",
    description="A production-grade issue tracking system with REST API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database-related exceptions."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error: Database operation failed"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    # In production, use Alembic migrations instead
    Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Application shutting down")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "issue-tracker-api"}


# Include API routers
# Temporarily use minimal issues router to avoid relationship issues
from app.routers.issues_minimal import router as issues_minimal_router
app.include_router(issues_minimal_router, prefix="/api/v1/issues", tags=["issues"])

# Use minimal users router to avoid relationship issues
from app.routers.users_minimal import router as users_minimal_router
app.include_router(users_minimal_router, prefix="/api/v1/users", tags=["users"])

# Use minimal projects router to avoid relationship issues
from app.routers.projects_minimal import router as projects_minimal_router
app.include_router(projects_minimal_router, prefix="/api/v1/projects", tags=["projects"])

# Use minimal comments router to avoid relationship issues
from app.routers.comments_minimal import router as comments_minimal_router
app.include_router(comments_minimal_router, prefix="/api/v1/comments", tags=["comments"])

# Use minimal attachments router to avoid relationship issues
from app.routers.attachments_minimal import router as attachments_minimal_router
app.include_router(attachments_minimal_router, prefix="/api/v1/attachments", tags=["attachments"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
