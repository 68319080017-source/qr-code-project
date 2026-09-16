import uuid
from sqlalchemy import Column, String, Text, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.database.session import Base
from app.models.base import TimeStampMixin, GUID

class AssetStatus(str, enum.Enum):
    NORMAL = "ปกติ"
    BROKEN = "ชำรุด"
    SOLD = "จำหน่ายแล้ว"
    REPAIRING = "รอซ่อม"
    PENDING_INSPECTION = "ค้างตรวจสอบ"
    LOST = "สูญหาย"

class Asset(Base, TimeStampMixin):
    __tablename__ = 'assets'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Identification
    asset_number = Column(String(100), unique=True, index=True, nullable=False)
    asset_code = Column(String(100), unique=True, index=True)
    qr_code_id = Column(String(255), unique=True, index=True)

    name = Column(String(255), index=True, nullable=False)
    description = Column(Text)

    # Classification
    category_id = Column(GUID(), ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    asset_type = Column(String(100))
    brand = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), index=True)

    # Vendors
    manufacturer = Column(String(255))
    vendor = Column(String(255))

    # Dates & Financials
    purchase_date = Column(Date)
    receive_date = Column(Date)
    warranty_expire_date = Column(Date)
    price = Column(Numeric(15, 2))
    budget_source = Column(String(150))
    fiscal_year = Column(String(4))

    # Location
    location_id = Column(GUID(), ForeignKey('locations.id', ondelete='SET NULL'), nullable=True)
    position_details = Column(String(255))

    # Ownership
    department = Column(String(150))
    responsible_user_id = Column(GUID(), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Status – stored as plain String for SQLite compatibility
    status = Column(String(50), default=AssetStatus.NORMAL.value, index=True)
    notes = Column(Text)

    # Files
    image_url = Column(String(500))
    attachments = Column(Text, default="[]")  # JSON text for portability

    # Relationships
    category = relationship('Category', back_populates='assets')
    location = relationship('Location', back_populates='assets')
    responsible_person = relationship('User', back_populates='assets')
    maintenance_logs = relationship('MaintenanceLog', back_populates='asset', cascade="all, delete-orphan")
    audit_logs = relationship('AuditLog', back_populates='asset', cascade="all, delete-orphan")
