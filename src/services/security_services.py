import datetime
import uuid

from fastapi import HTTPException, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from starlette import status

import infra.repositories.user_repository as user_repo
from constants import ENCRYPT_KEY, SECURITY_ALGORITHM, MAXIMUM_WRONG_PASSWORD_ATTEMPTS, ACCESS_TOKEN_EXPIRE_MINUTES, \
    REFRESH_TOKEN_EXPIRE_DAYS, CHANGE_PASSWORD_TOKEN_EXPIRE_MINUTES, USER_NOT_FOUND, \
    USER_INACTIVATED_FOR_MAX_ATTEMPTS, INVALID_CREDENTIALS, PASSWORDS_DO_NOT_MATCH, \
    PASSWORDS_ALREADY_USED, NOT_ALLOWED_TO_CHANGE_PASSWORD, INVALID_RESET_PASSWORD_TOKEN, USER_NOT_AUTHENTICATED, \
    INVALID_EXPIRED_PASSWORD_TOKEN, NOT_VALID_CREDENTIALS, REACTIVATED_USER_TOKEN_EXPIRE_DAYS
from domain.enums import State
from domain.users import User, ResetPasswordToken
from services import notification_services
from rest_api.dtos import ChangePasswordRequest, ReassignExpiredPasswordRequest, \
    ResetPasswordRequest

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="security/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=NOT_VALID_CREDENTIALS,
    )

    try:
        payload = jwt.decode(token, ENCRYPT_KEY, algorithms=[SECURITY_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user: User = user_repo.find_user_by_id(user_id)
    if user is None or user.state == State.INACTIVE:
        raise credentials_exception

    return user


def get_user_by_id(user_id: str):
    user: User = user_repo.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    return user


def login(form_data: OAuth2PasswordRequestForm, response: Response, source: str) -> str:
    user: User = user_repo.find_user_by_email(form_data.username)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_VALID_CREDENTIALS)

    password = user.get_current_active_password()
    if not user.verify_password(form_data.password):
        if password:
            password.password_attempts += 1

            if password.password_attempts >= MAXIMUM_WRONG_PASSWORD_ATTEMPTS:
                user.inactivate_user()
                user_repo.update_user(user)

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail=USER_INACTIVATED_FOR_MAX_ATTEMPTS)

            user_repo.update_user(user)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=INVALID_CREDENTIALS)

    password.password_attempts = 0
    user_repo.update_user(user)
    create_refresh_token(response, user, source)

    return create_access_token(user)


def create_access_token(user: User) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded_jwt = jwt.encode({'sub': user.id, 'exp': expire}, ENCRYPT_KEY, algorithm=SECURITY_ALGORITHM)

    return encoded_jwt


def create_refresh_token(response: Response, user: User, source: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    encoded_jwt = jwt.encode({'sub': user.id, 'exp': expire}, ENCRYPT_KEY, algorithm=SECURITY_ALGORITHM)

    user.add_refresh_token(encoded_jwt, source)
    user_repo.update_user(user)

    response.set_cookie(key='refresh_token', value=encoded_jwt, httponly=True, secure=True, samesite='strict',
                        expires=int((expire - datetime.datetime.utcnow()).total_seconds()))


def send_changed_password_notification(user: User, source: str):
    reset_token = ResetPasswordToken(str(uuid.uuid4()),
                                     datetime.datetime.utcnow() + datetime.timedelta(
                                         days=REACTIVATED_USER_TOKEN_EXPIRE_DAYS))
    user.reset_password_token = reset_token
    user_repo.update_user(user)

    notification_services.send_changed_password(user, source)


def change_password(user_id: str, change_password_request: ChangePasswordRequest, refresh_token: str, source: str):
    user: User = user_repo.find_user_by_id(user_id)

    if not user.verify_password(change_password_request.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=PASSWORDS_DO_NOT_MATCH)

    if user.already_used_password(change_password_request.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=PASSWORDS_ALREADY_USED)

    user.update_password(change_password_request.new_password)
    revoke_other_refresh_tokens(user, refresh_token)

    send_changed_password_notification(user, source)


def revoke_other_refresh_tokens(user: User, refresh_token: str):
    for rt in user.refresh_tokens:
        if rt.token == refresh_token:
            user.refresh_tokens = [rt]


def forgot_password(email: str):
    user: User = user_repo.find_user_by_email(email)

    if not user:
        return

    reset_token = ResetPasswordToken(str(uuid.uuid4()),
                                     datetime.datetime.utcnow() + datetime.timedelta(
                                         minutes=CHANGE_PASSWORD_TOKEN_EXPIRE_MINUTES))
    user.reset_password_token = reset_token
    notification_services.send_forgot_password(user, CHANGE_PASSWORD_TOKEN_EXPIRE_MINUTES)

    user_repo.update_user(user)


def reset_password(reset_password_request: ResetPasswordRequest, source: str):
    user: User = user_repo.find_user_by_id(reset_password_request.user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    if not user.reset_password_token:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail=NOT_ALLOWED_TO_CHANGE_PASSWORD)

    if user.reset_password_token.token != reset_password_request.reset_password_token or \
            datetime.datetime.utcnow() > user.reset_password_token.expiration_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=INVALID_RESET_PASSWORD_TOKEN)

    if user.already_used_password(reset_password_request.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=PASSWORDS_ALREADY_USED)

    user.update_password(reset_password_request.new_password)
    user.reset_password_token = None
    user.refresh_tokens = []

    send_changed_password_notification(user, source)


def reassign_expired_password(reassign_expired_password_request: ReassignExpiredPasswordRequest):
    user: User = user_repo.find_user_by_id(reassign_expired_password_request.user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    if not user.expired_password_token:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail=NOT_ALLOWED_TO_CHANGE_PASSWORD)

    if user.expired_password_token != reassign_expired_password_request.expired_password_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=INVALID_EXPIRED_PASSWORD_TOKEN)

    user.update_password(reassign_expired_password_request.password)
    user.expired_password_token = None
    user_repo.update_user(user)


def refresh(refresh_token: str = Cookie(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=NOT_VALID_CREDENTIALS
    )

    try:
        payload = jwt.decode(refresh_token, ENCRYPT_KEY, algorithms=[SECURITY_ALGORITHM])
        refresh_token_user_id: str = payload.get("sub")
    except Exception:
        raise credentials_exception

    found_refresh_token = False
    user: User = user_repo.find_user_by_id(refresh_token_user_id)
    if user.refresh_tokens:
        for rt in user.refresh_tokens:
            if refresh_token == rt.token:
                found_refresh_token = True
                break

    if not found_refresh_token:
        raise credentials_exception

    return create_access_token(user)


def logout(response: Response, refresh_token: str):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=USER_NOT_AUTHENTICATED)

    try:
        payload = jwt.decode(refresh_token, ENCRYPT_KEY, algorithms=[SECURITY_ALGORITHM])
        refresh_token_user_id: str = payload.get("sub")
    except ExpiredSignatureError:
        refresh_token_user_id: str = jwt.get_unverified_claims(refresh_token).get('sub')
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
        )

    user: User = user_repo.find_user_by_id(refresh_token_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    updated_refresh_tokens = []
    for rt in user.refresh_tokens:
        if rt.token != refresh_token:
            updated_refresh_tokens.append(rt)

    user.refresh_tokens = updated_refresh_tokens
    user_repo.update_user(user)

    response.delete_cookie(key='refresh_token')
