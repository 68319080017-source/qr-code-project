from fastapi import APIRouter

from app.routers import users, auth, categories, locations, assets, upload, maintenance, audit

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
