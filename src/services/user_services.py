import datetime
import logging
import uuid
from datetime import datetime
from typing import List, Dict

from fastapi import HTTPException
from starlette import status

import infra.repositories.user_repository as user_repo
from constants import *
from domain.enums import Environment, State, UserRole
from domain.users import User, UserInvitation, UserPassword, ResetPasswordToken
from rest_api.dtos import CreateUserRequest, InviteUserRequest, UpdateUserContactInfoRequest
from services import notification_services


def get_user_by_id(user_id: str) -> User:
    user: User = user_repo.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=USER_NOT_FOUND)

    return user


def load_inactive_users() -> List[Dict]:
    users: List[User] = user_repo.find_users()

    inactive_users: List[Dict] = []
    for user in users:
        if user.state == State.INACTIVE:
            user: User = user_repo.find_user_by_id(user.id)

            inactive_users.append(user.to_api_response())

    return inactive_users


def reactivate_user(user_id: str):
    user: User = get_user_by_id(user_id)

    user.state = State.ACTIVE
    reset_token = ResetPasswordToken(str(uuid.uuid4()),
                                     datetime.datetime.utcnow() + datetime.timedelta(
                                         days=REACTIVATED_USER_TOKEN_EXPIRE_DAYS))
    user.reset_password_token = reset_token
    notification_services.send_reactivated_account(user)

    user_repo.update_user(user)


def get_users_info() -> List[Dict]:
    users: List[User] = user_repo.find_users()

    users_data: List[Dict] = []
    for user in users:
        if user.role != UserRole.ADMIN:
            users_data.append(user.to_api_response())

    return users_data


def invite_new_user(user: User, invite_user_request: InviteUserRequest):
    if user_repo.find_user_by_email(invite_user_request.new_user_email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=USER_ALREADY_EXIST_WITH_EMAIL)

    new_invitation = UserInvitation(invite_user_request.new_user_email, str(uuid.uuid4()))
    if user.invitations:
        for invitations_sent in user.invitations:
            if invitations_sent.new_user_email == invite_user_request.new_user_email:
                new_invitation = invitations_sent
                user.invitations.remove(new_invitation)

    user.invitations.append(new_invitation)

    notification_services.send_invitation(user, invite_user_request.new_user_email,
                                          new_invitation, invite_user_request.invitation_language)

    user_repo.update_user(user)


def get_sponsor_info(sponsor_user_id: str, invitation_code: str):
    sponsor_user = user_repo.find_user_by_id(sponsor_user_id)

    if not sponsor_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    invitation = None
    if not sponsor_user.invitations:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=INVALID_INVITATION)

    for i in sponsor_user.invitations:
        if i.validation_code == invitation_code:
            invitation = i

    if not invitation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=INVALID_INVITATION)

    user_already_created = user_repo.find_user_by_email(invitation.new_user_email)
    if user_already_created:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=INVITATION_ALREADY_USED)

    sponsor = get_user_by_id(sponsor_user.id)
    return {
        'given_names': sponsor.given_names.split()[0],
        'family_names': sponsor.family_names.split()[0],
        'email': sponsor.email
    }


def create_user(create_user_request: CreateUserRequest):
    if user_repo.find_user_by_email(create_user_request.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=USER_ALREADY_EXIST_WITH_USERNAME)

    if APP_ENVIRONMENT == Environment.PROD.name:
        sponsor_user = user_repo.find_user_by_id(create_user_request.sponsor_user_id)
        if not sponsor_user or not sponsor_user.invitations:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=SPONSOR_NOT_FOUND)

        found_invitation = False
        for invitation in sponsor_user.invitations:
            if invitation.validation_code == create_user_request.invitation_code and \
                    invitation.new_user_email == create_user_request.email:
                found_invitation = True

        if not found_invitation:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=INVALID_INVITATION)

    password = UserPassword(password=create_user_request.password)
    user = User(
        id=str(uuid.uuid4()),
        email=create_user_request.email,
        given_names=create_user_request.given_names,
        family_names=create_user_request.family_names,
        nickname=create_user_request.nickname,
        language=create_user_request.language,
        role=create_user_request.user_role,
        passwords=[password],
        anti_phishing_phrase=create_user_request.anti_phishing_phrase,
        state=State.ACTIVE
    )

    user_repo.insert_user(user)

    for u in user_repo.find_users():
        if u.role == UserRole.ADMIN:
            notification_services.send_created_account(u, user)


def update_user_contact_info(update_user_contact_info_request: UpdateUserContactInfoRequest,
                             user: User):
    user.nickname = update_user_contact_info_request.nickname
    user.anti_phishing_phrase = update_user_contact_info_request.anti_phishing_phrase
    user_repo.update_user(user)


def get_secure_user_data(user: User) -> Dict:
    user = get_user_by_id(user.id)
    data = user.to_api_response()
    data['email'] = user.email
    data['anti_phishing_phrase'] = user.anti_phishing_phrase

    return data


def check_expired_passwords():
    logging.info('Checking expired passwords')
    users = user_repo.find_users()
    for user in users:
        password = user.get_current_active_password()

        if password:
            days_to_expire = (password.expiration_date - datetime.utcnow()).days

            if datetime.utcnow() >= password.expiration_date:
                password.state = State.INACTIVE
                user.expired_password_token = str(uuid.uuid4())

                notification_services.send_password_expired(user)
                user_repo.update_user(user)

            elif days_to_expire <= REMAINING_PASSWORD_DAYS_TO_SEND_NOTIFICATION:
                notification_services.send_password_near_to_expire(user, days_to_expire)


def get_users(current_user: User) -> List:
    users: List[User] = user_repo.find_users()
    users_list = []
    for user in users:
        if user.role != UserRole.ADMIN and user.state != State.INACTIVE and current_user.id != user.id:
            users_list.append(user.to_simple_data())

    return users_list
