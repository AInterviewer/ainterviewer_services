from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from constants import DATETIME_FORMAT


@dataclass
class Event:
    user: str
    action: str
    data: Dict
    error: bool
    exception: Optional[str]
    date: datetime

    def to_dict(self):
        return {
            'date': self.date.strftime(DATETIME_FORMAT),
            'user': self.user,
            'action': self.action,
            'data': str(self.data),
            'error': self.error,
            'exception': self.exception if self.exception else None
        }
