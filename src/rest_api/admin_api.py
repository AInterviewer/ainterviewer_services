from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

import services.admin_services as admin_serv
import services.security_services as sec_serv
import services.user_services as user_serv
import services.audit_services as audit
from domain.enums import UserRole
from domain.users import User
from services.dtos import SendMessageToUserRequest, \
    SendMessageToAllUsersRequest

admin_api = APIRouter()


def check_allowed_admin_action(user: User):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not allowed action for this user')


@admin_api.get('/inactive_users', tags=['Admin'], status_code=status.HTTP_200_OK)
async def inactive_users(user: User = Depends(sec_serv.get_current_user)) -> List[Dict]:
    """Returns a list of inactive users"""
    check_allowed_admin_action(user)
    return user_serv.load_inactive_users()


@admin_api.post('/reactivate_user', tags=['Admin'], status_code=status.HTTP_200_OK)
async def reactivate_user(user_id: str, user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Reactivate a user"""
    try:
        check_allowed_admin_action(user)
        user_serv.reactivate_user(user_id)
        return True
    finally:
        audit.audit_entity(user.id, 'activated_user', {'user_id': user_id})


@admin_api.get('/users_info', tags=['Admin'], status_code=status.HTTP_200_OK)
async def get_users_info(user: User = Depends(sec_serv.get_current_user)) -> List[Dict]:
    """Returns a list of users info"""
    check_allowed_admin_action(user)
    return user_serv.get_users_info()


@admin_api.post('/send_message_to_user', tags=['Admin'], status_code=status.HTTP_200_OK)
async def send_message_to_user(send_message_request: SendMessageToUserRequest,
                               user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Send a message to a user"""
    try:
        check_allowed_admin_action(user)
        admin_serv.send_message_to_user(send_message_request)
        return True
    finally:
        audit.audit_entity(user.id, 'sent_message_to_user', send_message_request.to_audit())


@admin_api.post('/send_message_to_all_users', tags=['Admin'], status_code=status.HTTP_200_OK)
async def send_message_to_user(send_message_request: SendMessageToAllUsersRequest,
                               user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Send a message to all users that has the language selected"""
    try:
        check_allowed_admin_action(user)
        admin_serv.send_message_to_all_users(send_message_request)
        return True
    finally:
        audit.audit_entity(user.id, 'sent_message_to_all_users', send_message_request.to_audit())
