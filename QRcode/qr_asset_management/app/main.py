"""
Application Entry Point
Main FastAPI application setup and configuration
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.api.v1 import router as api_router
# from app.interfaces.web import web_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Application factory function for creating FastAPI app instances.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="QR Asset Management System",
        description="Enterprise-grade QR code asset management platform",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        generate_schemas=True,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add security middlewares in production
    if settings.environment == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Add trusted hosts middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    # Include routers
    app.include_router(api_router, prefix="/api/v1")
    # app.include_router(web_router)  # <-- ปิดบรรทัดนี้แล้ว

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring"""
        return {"status": "healthy", "version": "0.1.0"}

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to QR Asset Management System",
            "docs": "/docs",
            "version": "0.1.0"
        }

    logger.info("Application initialized successfully")
    return app


# Create application instance
app = create_app()