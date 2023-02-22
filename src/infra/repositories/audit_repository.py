from domain.audit import Event
from infra.repositories.general_repository import CLIENT

AUDIT_COLLECTION = CLIENT.audit


def insert_audit_event(event: Event):
    AUDIT_COLLECTION.insert_one(event.to_dict())
