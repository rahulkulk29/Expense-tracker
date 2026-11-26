import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.api.expenses import router as expenses_router
from app.db.session import Base, engine
from app.models import expense as _expense_model  # noqa: F401 - register ORM models before create_all


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize database tables on startup."""
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        # Allow app startup even if DB is temporarily unreachable; requests will return 503.
        pass
    yield


app = FastAPI(
    title="Expense Tracker API",
    description="Single-user personal Expense Tracker REST API built with FastAPI and PostgreSQL.",
    version="1.0.0",
    lifespan=lifespan,
)

raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


@app.exception_handler(OperationalError)
async def database_unavailable_handler(_request: Request, _exc: OperationalError) -> JSONResponse:
    """Return a safe 503 response when PostgreSQL cannot be reached."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service unavailable"},
    )


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(_request: Request, _exc: SQLAlchemyError) -> JSONResponse:
    """Return a safe 500 response for unexpected database errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Prevent internal stack traces from leaking to API clients."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Basic liveness check."""
    return {"status": "healthy"}


app.include_router(expenses_router, prefix="/api/v1")

