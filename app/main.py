from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging, setup_telemetry
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.middlewares.request_logger import RequestLoggerMiddleware

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="FastAPI template with security and essential modules",
    version="1.0.0",
)

# Setup OpenTelemetry
tracer = setup_telemetry(app)

# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggerMiddleware)

# Add rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint for kubernetes/monitoring."""
    logger.info("Health check endpoint called")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the application")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)