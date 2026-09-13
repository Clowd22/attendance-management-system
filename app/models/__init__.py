# =============================================================================
# モデル一括読み込み
# -----------------------------------------------------------------------------
# このファイルを import するだけで、すべてのモデルが Base.metadata に登録される。
# Alembic のマイグレーションや seed はここを経由してモデルを認識する。
# =============================================================================
from app.db.base import Base
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_type import LeaveType
from app.models.work_schedule import WorkSchedule

__all__ = ["Base", "Department", "Employee", "LeaveType", "WorkSchedule"]