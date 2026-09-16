from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database.session import get_db
from app.models.category import Location as LocationModel
from app.schemas.category import Location, LocationCreate, LocationUpdate
from app.routers.deps import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Location])
def read_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    locations = db.query(LocationModel).offset(skip).limit(limit).all()
    return locations

@router.post("/", response_model=Location)
def create_location(
    location_in: LocationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    location = LocationModel(**location_in.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location
