import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import TimeStampMixin, GUID

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', GUID(), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', GUID(), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

class Role(Base, TimeStampMixin):
    __tablename__ = 'roles'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))

    users = relationship('User', secondary=user_roles, back_populates='roles')

class User(Base, TimeStampMixin):
    __tablename__ = 'users'

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    roles = relationship('Role', secondary=user_roles, back_populates='users')
    assets = relationship('Asset', back_populates='responsible_person')
