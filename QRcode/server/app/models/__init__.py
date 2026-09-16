from app.database.session import Base
from app.models.user import User, Role, user_roles
from app.models.category import Category, Location
from app.models.asset import Asset
from app.models.logs import MaintenanceLog, AuditLog

# Ensure all models are imported so Alembic can discover them
