from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings

def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Set all CORS enabled origins
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Ensure directories exist
    for d in ["app/static", "uploads", "qrcodes", "reports"]:
        os.makedirs(d, exist_ok=True)

    # Static files
    application.mount("/static", StaticFiles(directory="app/static"), name="static")
    application.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    application.mount("/qrcodes", StaticFiles(directory="qrcodes"), name="qrcodes")
    application.mount("/reports", StaticFiles(directory="reports"), name="reports")

    # Auto-create database tables (for SQLite fallback)
    from app.database.session import engine, Base
    from app.models import User, Role, Category, Location, Asset, MaintenanceLog, AuditLog  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Seed default superuser if not exists
    _seed_initial_data()

    # Include routers
    from app.routers import api_router, pages
    application.include_router(api_router, prefix=settings.API_V1_STR)
    application.include_router(pages.router)

    return application


def _seed_initial_data():
    """Create a default superadmin user if the users table is empty."""
    from app.database.session import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash
    import logging

    logger = logging.getLogger(__name__)
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            admin = User(
                email="admin@qrasset.local",
                hashed_password=get_password_hash("admin1234"),
                first_name="Super",
                last_name="Admin",
                is_active=True,
                is_superuser=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Seeded default superadmin: admin@qrasset.local / admin1234")
    except Exception as e:
        logger.warning(f"Seed data skipped: {e}")
        db.rollback()
    finally:
        db.close()


app = get_application()
