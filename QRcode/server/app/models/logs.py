import uuid
from sqlalchemy import Column, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.database.session import Base
from app.models.base import TimeStampMixin, GUID

class MaintenanceStatus(str, enum.Enum):
    PENDING = "รอซ่อม"
    IN_PROGRESS = "กำลังซ่อม"
    COMPLETED = "ซ่อมเสร็จแล้ว"
    CANCELLED = "ยกเลิก"

class MaintenanceLog(Base, TimeStampMixin):
    __tablename__ = 'maintenance_logs'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    asset_id = Column(GUID(), ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    reported_by_id = Column(GUID(), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    issue_description = Column(Text, nullable=False)
    status = Column(String(50), default=MaintenanceStatus.PENDING.value, index=True)

    repair_cost = Column(Numeric(15, 2))
    repair_details = Column(Text)

    image_before_url = Column(String(500))
    image_after_url = Column(String(500))

    asset = relationship('Asset', back_populates='maintenance_logs')
    reported_by = relationship('User')

class AuditStatus(str, enum.Enum):
    NORMAL = "ปกติ"
    BROKEN = "ชำรุด"
    LOST = "สูญหาย"
    TO_BE_SOLD = "รอจำหน่าย"

class AuditLog(Base, TimeStampMixin):
    __tablename__ = 'audit_logs'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    asset_id = Column(GUID(), ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    audited_by_id = Column(GUID(), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    audit_cycle = Column(String(100))
    status_found = Column(String(50), nullable=False)

    notes = Column(Text)
    image_url = Column(String(500))

    asset = relationship('Asset', back_populates='audit_logs')
    audited_by = relationship('User')
