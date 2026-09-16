from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database.session import get_db
from app.models.category import Category as CategoryModel
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.routers.deps import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    categories = db.query(CategoryModel).offset(skip).limit(limit).all()
    return categories

@router.post("/", response_model=Category)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    category = db.query(CategoryModel).filter(CategoryModel.name == category_in.name).first()
    if category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    category = CategoryModel(**category_in.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
