from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.connection import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.repositories.user_repo import UserRepository
from app.auth.dependencies import get_current_active_user, RoleChecker
from app.core import security

router = APIRouter()

allow_manage_users = RoleChecker(["Super Admin", "Admin"])

# =========================================================
# REAL-TIME ADMIN TRACKER (ความจำแรมชั่วคราวบน Server)
# =========================================================
active_admins = {}

@router.post("/ping")
async def ping_active_admin(request: Request):
    """
    ดักจับสัญญาณออนไลน์ชั่วคราวจากเบราว์เซอร์/มือถือ เพื่อนำไปแสดงผล Real-time บนหน้าเว็บ
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "Unknown Device")
    
    # จำแนกประเภทอุปกรณ์
    if any(m in user_agent for m in ["iPhone", "Android", "Mobile"]):
        device_type = "Mobile Browser"
    elif "Chrome" in user_agent:
        device_type = "Google Chrome (Desktop)"
    else:
        device_type = "Web Browser"

    # อัปเดตข้อมูลของผู้ใช้ล่าสุด
    active_admins[client_ip] = {
        "ip": client_ip,
        "device": device_type,
        "last_seen": datetime.now().strftime("%H:%M:%S")
    }
    
    # คืนค่ารันลำดับ admin01, admin02...
    admin_list = []
    for idx, (ip, data) in enumerate(active_admins.items(), start=1):
        admin_list.append({
            "code": f"admin{idx:02d}",
            "device": data["device"],
            "last_seen": data["last_seen"],
            "is_me": (ip == client_ip)
        })
        
    return {"active_count": len(admin_list), "admins": admin_list}


# =========================================================
# STANDARD CRUD USER ROUTES
# =========================================================

@router.get("/", response_model=List[User])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(allow_manage_users),
) -> Any:
    """
    Retrieve users.
    """
    result = await db.execute(select(UserModel).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=User)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(allow_manage_users),
) -> Any:
    """
    Create new user.
    """
    repo = UserRepository(db)
    user = await repo.get_by_username(user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await repo.create(user_in)
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(allow_manage_users),
) -> Any:
    """
    Update a user.
    """
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = security.get_password_hash(update_data["password"])
        del update_data["password"]
        
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user