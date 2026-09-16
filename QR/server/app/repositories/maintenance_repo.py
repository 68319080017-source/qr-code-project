from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.maintenance import Maintenance
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate

class MaintenanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, maintenance_id: int) -> Optional[Maintenance]:
        result = await self.db.execute(select(Maintenance).filter(Maintenance.id == maintenance_id))
        return result.scalars().first()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, asset_id: Optional[int] = None
    ) -> List[Maintenance]:
        query = select(Maintenance)
        if asset_id:
            query = query.filter(Maintenance.asset_id == asset_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: MaintenanceCreate, reporter_id: Optional[int] = None) -> Maintenance:
        db_obj = Maintenance(**obj_in.model_dump(), reporter_id=reporter_id)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Maintenance, obj_in: MaintenanceUpdate) -> Maintenance:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
