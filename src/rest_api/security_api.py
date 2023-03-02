import httpagentparser
from fastapi import APIRouter, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request

import services.security_services as sec_serv
import services.audit_services as audit
from domain.users import User
from rest_api.dtos import ChangePasswordRequest, ReassignExpiredPasswordRequest, \
    ForgotPasswordRequest, ResetPasswordRequest

security_api = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


def get_os_and_browser(request: Request):
    user_agent = httpagentparser.detect(request.headers.get('user-agent'))
    return f'{user_agent.get("os").get("name")}' \
           f'{" " + user_agent.get("dist").get("name") if user_agent.get("dist") else ""}, ' \
           f'{user_agent.get("browser").get("name")}'


@security_api.post('/login', tags=['Security'], status_code=status.HTTP_200_OK, response_model=Token)
async def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login a user in the application"""
    try:
        return {"access_token": sec_serv.login(form_data, response, get_os_and_browser(request)),
                "token_type": "bearer"}
    finally:
        audit.audit_entity('', 'logged_in', {'user': form_data.username, 'source': get_os_and_browser(request)})


@security_api.post('/logout', tags=['Security'], status_code=status.HTTP_200_OK)
async def logout(response: Response, refresh_token: str = Cookie(None)) -> bool:
    """Logout a user from the application"""
    sec_serv.logout(response, refresh_token)
    return True


@security_api.patch('/change_password', tags=['Security'], status_code=status.HTTP_200_OK)
async def change_password(change_password_request: ChangePasswordRequest,
                          request: Request,
                          refresh_token: str = Cookie(None),
                          user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Changes a user's password"""
    try:
        sec_serv.change_password(user.id, change_password_request, refresh_token, get_os_and_browser(request))
        return True
    finally:
        audit.audit_entity(user.id, 'changed_password', {'source': get_os_and_browser(request)})


@security_api.patch('/forgot_password', tags=['Security'], status_code=status.HTTP_200_OK)
async def forgot_password(forgot_password_request: ForgotPasswordRequest) -> bool:
    """Sends a message to reset the user's password"""
    try:
        sec_serv.forgot_password(forgot_password_request.email)
        return True
    finally:
        audit.audit_entity('', 'forgot_password', {'email': forgot_password_request.email})


@security_api.patch('/reset_password', tags=['Security'], status_code=status.HTTP_200_OK)
async def reset_password(reset_password_request: ResetPasswordRequest,
                         request: Request) -> bool:
    """Reset the password for a user"""
    try:
        sec_serv.reset_password(reset_password_request, get_os_and_browser(request))
        return True
    finally:
        audit.audit_entity('', 'reset_password',
                           {'user_id': reset_password_request.user_id, 'source': get_os_and_browser(request)})


@security_api.patch('/reassign_expired_password', tags=['Security'], status_code=status.HTTP_200_OK)
async def reassign_expired_password(reassign_expired_password_request: ReassignExpiredPasswordRequest) -> bool:
    """Reassign a new password for a user who has the password expired"""
    try:
        sec_serv.reassign_expired_password(reassign_expired_password_request)
        return True
    finally:
        audit.audit_entity('', 'reassigned_expired_password', {'user_id': reassign_expired_password_request.user_id})


@security_api.patch('/refresh', tags=['Security'], status_code=status.HTTP_200_OK)
async def refresh(new_token: str = Depends(sec_serv.refresh)):
    """Refresh a JWT token"""
    return {"access_token": new_token, "token_type": "bearer"}
