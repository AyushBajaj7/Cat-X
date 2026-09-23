"""Main application entrypoint for API Gateway (Port 8000)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import router as gateway_router

app = FastAPI(
    title="CAT Operator Shift Twin - API Gateway",
    description="Central API Gateway routing and aggregating between Frontend, Safety, Operations, and Training microservices.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gateway_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.service_port)
