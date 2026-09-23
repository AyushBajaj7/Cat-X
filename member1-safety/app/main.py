"""Main application entrypoint for Safety Service (Port 8001)."""

from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import router as safety_router

app = FastAPI(
    title="CAT Operator Shift Twin - Safety Service",
    description="Microservice responsible for safety alerts, seatbelt compliance, incident logging, and behavior analysis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(safety_router)


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
