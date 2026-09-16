from app.models.base import Base
from app.models.user import User
from app.models.asset import Asset
from app.models.maintenance import Maintenance
from app.models.log import ActivityLog

# สร้างตัวแปรหลอกไว้รองรับพวก router ที่สั่ง import models
class ModelsContainer:
    Base = Base
    User = User
    Asset = Asset
    Maintenance = Maintenance
    ActivityLog = ActivityLog

models = ModelsContainer()

__all__ = ["Base", "User", "Asset", "Maintenance", "ActivityLog", "models"]