"""Database models package.

Importing from here (rather than the individual module files) ensures
every model is registered on `db.metadata` before `db.create_all()`
runs in the application factory.
"""

from app.models.crowd_report import DENSITY_LEVELS, CrowdReport
from app.models.staff_task import TASK_PRIORITIES, TASK_STATUSES, StaffTask
from app.models.sustainability_log import EMISSION_FACTORS, SustainabilityLog
from app.models.user import User

__all__ = [
    "User",
    "CrowdReport",
    "DENSITY_LEVELS",
    "StaffTask",
    "TASK_STATUSES",
    "TASK_PRIORITIES",
    "SustainabilityLog",
    "EMISSION_FACTORS",
]
