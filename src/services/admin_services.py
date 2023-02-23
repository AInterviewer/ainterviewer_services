from fastapi import HTTPException
from starlette import status

import infra.repositories.user_repository as user_repo
import infra.repositories.general_repository as general_repo
from constants import USER_NOT_FOUND
from domain import utils
from domain.enums import UserRole
from services import notification_services
from services.dtos import SendMessageToUserRequest, SendMessageToAllUsersRequest


def start_app():
    if not general_repo.ainterview_database_exists():
        admin_user = utils.create_admin()
        user_repo.insert_user(admin_user)


def send_message_to_user(send_message_request: SendMessageToUserRequest):
    user = user_repo.find_user_by_id(send_message_request.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    notification_services.send_message_to_user(user, send_message_request.message,
                                               send_message_request.subject)


def send_message_to_all_users(send_message_request: SendMessageToAllUsersRequest):
    for user in user_repo.find_users():
        if user.role == UserRole.ADMIN or user.language != send_message_request.language:
            continue

        notification_services.send_message_to_user(user, send_message_request.message, send_message_request.subject)
