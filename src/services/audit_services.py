import datetime
import sys
from typing import Dict

import infra.repositories.audit_repository as audit_repo
from domain.audit import Event


def audit_entity(user_id: str, action: str, data: Dict):
    error_message = None
    if sys.exc_info()[0]:
        if str(sys.exc_info()[1]) != '':
            error_message = str(sys.exc_info()[1])
        else:
            error_message = sys.exc_info()[1].detail

    audit_repo.insert_audit_event(
        Event(
            user=user_id,
            action=action,
            data=data,
            error=sys.exc_info()[0] is not None,
            exception=error_message,
            date=datetime.datetime.utcnow()
        )
    )
