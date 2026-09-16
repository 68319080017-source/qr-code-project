"""
API v1 Package
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, assets, categories, roles

router = APIRouter()

# Include all endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(assets.router, prefix="/assets", tags=["Assets"])
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
router.include_router(roles.router, prefix="/roles", tags=["Roles"])

__all__ = ["router"]