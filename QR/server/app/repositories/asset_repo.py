from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate

class AssetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, asset_id: int) -> Optional[Asset]:
        result = await self.db.execute(select(Asset).filter(Asset.id == asset_id))
        return result.scalars().first()

    async def get_by_code(self, asset_code: str) -> Optional[Asset]:
        result = await self.db.execute(select(Asset).filter(Asset.asset_code == asset_code))
        return result.scalars().first()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[Asset]:
        query = select(Asset)
        if search:
            query = query.filter(
                or_(
                    Asset.asset_code.ilike(f"%{search}%"),
                    Asset.name.ilike(f"%{search}%"),
                    Asset.serial_number.ilike(f"%{search}%"),
                    Asset.building.ilike(f"%{search}%"),
                    Asset.room.ilike(f"%{search}%"),
                    Asset.responsible_person.ilike(f"%{search}%"),
                )
            )
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, asset_in: AssetCreate) -> Asset:
        db_obj = Asset(**asset_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Asset, obj_in: AssetUpdate) -> Asset:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, asset_id: int) -> Optional[Asset]:
        obj = await self.get_by_id(asset_id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj
