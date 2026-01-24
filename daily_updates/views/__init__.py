from .daily_update import DailyUpdateViewSet
from .web import (
    list_daily_updates, create_daily_update,
    update_daily_update, delete_daily_update
)

__all__ = [
    'DailyUpdateViewSet',
    'list_daily_updates', 'create_daily_update',
    'update_daily_update', 'delete_daily_update'
]
