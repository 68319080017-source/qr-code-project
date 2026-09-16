import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import TimeStampMixin, GUID

class Category(Base, TimeStampMixin):
    __tablename__ = 'categories'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), unique=True, index=True, nullable=False)
    description = Column(Text)

    assets = relationship('Asset', back_populates='category')

class Location(Base, TimeStampMixin):
    __tablename__ = 'locations'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    building = Column(String(100), nullable=False)
    floor = Column(String(50))
    room = Column(String(100))
    description = Column(Text)

    assets = relationship('Asset', back_populates='location')
