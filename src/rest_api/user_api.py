from typing import Dict

from fastapi import APIRouter, Depends
from starlette import status

import services.security_services as sec_serv
import services.user_services as user_serv
import services.audit_services as audit
from domain.users import User
from services.dtos import InviteUserRequest, CreateUserRequest, UpdateUserContactInfoRequest

users_api = APIRouter()


@users_api.post('/invite_user', tags=['Users'], status_code=status.HTTP_201_CREATED)
async def invite_user(invite_user_request: InviteUserRequest,
                      user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Send an invitation to a new user"""
    try:
        user_serv.invite_new_user(user, invite_user_request)
        return True
    finally:
        audit.audit_entity(user.id, 'invited_user', invite_user_request.to_audit())


@users_api.get('/sponsor_info', tags=['Users'], status_code=status.HTTP_200_OK)
async def get_sponsor_info(sponsor_user_id: str, invitation_code: str) -> Dict:
    """Gets the basic info of the sponsor"""
    return user_serv.get_sponsor_info(sponsor_user_id, invitation_code)


@users_api.post('', tags=['Users'], status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest) -> bool:
    """Creates a new user"""
    try:
        user_serv.create_user(create_user_request)
        return True
    finally:
        audit.audit_entity('', 'created_user', create_user_request.to_audit())


@users_api.get('', tags=['Users'], status_code=status.HTTP_200_OK)
async def get_user(user: User = Depends(sec_serv.get_current_user)) -> Dict:
    """Gets a user"""
    return user_serv.get_secure_user_data(user)


@users_api.patch('/contact_info', tags=['Users'], status_code=status.HTTP_200_OK)
async def update_user_contact_info(update_user_contact_info_request: UpdateUserContactInfoRequest,
                                   user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Updates a user contact info"""
    try:
        user_serv.update_user_contact_info(update_user_contact_info_request, user)
        return True
    finally:
        audit.audit_entity(user.id, 'updated_user_contact_info', update_user_contact_info_request.to_audit())
