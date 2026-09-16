from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None

class Category(CategoryBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class LocationBase(BaseModel):
    building: str
    floor: Optional[str] = None
    room: Optional[str] = None
    description: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    building: Optional[str] = None

class Location(LocationBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
