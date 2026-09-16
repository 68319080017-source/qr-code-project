import sys
from app.schemas.asset import *
from app.schemas.maintenance import *
from app.schemas.token import *
from app.schemas.user import *

# ชี้ให้การเรียก app.schemas (ตัวมันเอง) มีค่าเท่ากับ module นี้โดยตรง
# ทำให้การสั่ง from app.schemas import schemas แล้วเรียก schemas.AssetOut ใช้งานได้ทันที
sys.modules['app.schemas.schemas'] = sys.modules[__name__]