"""Main application entrypoint for Safety Service (Port 8001)."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .database import init_db
from .models import ErrorCode, ErrorResponseModel
from .routes import router as safety_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("safety.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan."""
    logger.info(f"Starting {settings.service_name} on port {settings.service_port}...")
    if settings.db_auto_create:
        try:
            init_db()
        except Exception as e:
            logger.warning(f"Database initialization warning: {e}")
    yield
    logger.info(f"Shutting down {settings.service_name}...")


app = FastAPI(
    title="CAT Operator Shift Twin - Safety Service",
    description=(
        "Microservice responsible for continuous safety evaluation, seatbelt compliance, "
        "proximity hazard monitoring, incident lifecycle tracking, behavioral anomaly detection, "
        "and operational constraint signals for CAT Trajectory."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Safety API router
app.include_router(safety_router)


# Global Exception Handlers conforming to shared error.schema.json


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format request validation errors according to error.schema.json."""
    error_payload = ErrorResponseModel(
        error_code=ErrorCode.VALIDATION_ERROR,
        message="Request payload failed schema validation",
        timestamp=datetime.now(timezone.utc),
        details={"errors": exc.errors()},
        path=str(request.url.path),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_payload.model_dump(mode="json"),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Format HTTP errors according to error.schema.json."""
    code_map = {
        400: ErrorCode.VALIDATION_ERROR,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
        502: ErrorCode.BAD_GATEWAY,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }
    error_code = code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)

    error_payload = ErrorResponseModel(
        error_code=error_code,
        message=str(exc.detail),
        timestamp=datetime.now(timezone.utc),
        path=str(request.url.path),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload.model_dump(mode="json"),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Format unexpected errors according to error.schema.json."""
    logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
    error_payload = ErrorResponseModel(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="An unexpected internal server error occurred",
        timestamp=datetime.now(timezone.utc),
        details={"error_type": type(exc).__name__},
        path=str(request.url.path),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload.model_dump(mode="json"),
    )


@app.get("/api/v1/health", tags=["health"])
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "HEALTHY",
        "service": settings.service_name,
        "port": settings.service_port,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.service_port)
