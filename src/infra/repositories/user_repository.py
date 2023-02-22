from typing import Dict, List

from domain import utils
from domain.enums import State, UserRole, Language
from domain.users import User, \
    UserInvitation, ResetPasswordToken, UserPassword, RefreshToken
from infra.repositories.general_repository import CLIENT

USERS_COLLECTION = CLIENT.users


def insert_user(user: User):
    USERS_COLLECTION.insert_one(user.to_dict())


def update_user(user: User):
    USERS_COLLECTION.update_one(
        {'_id': user.id},
        {'$set': {
            'email': utils.encrypt_message(user.email),
            'given_names': utils.encrypt_message(user.given_names),
            'family_names': utils.encrypt_message(user.family_names),
            'nickname': utils.encrypt_message(user.nickname),
            'language': utils.encrypt_message(user.language.name),
            'anti_phishing_phrase': utils.encrypt_message(user.anti_phishing_phrase),
            'role': utils.encrypt_message(user.role.name),
            'state': utils.encrypt_message(user.state.name),
            'passwords': [password.to_dict() for password in user.passwords],
            'refresh_tokens': [refresh_token.to_dict() for refresh_token in
                               user.refresh_tokens] if user.refresh_tokens else None,
            'invitations': [invitation.to_dict() for invitation in user.invitations] if user.invitations else None,
            'reset_password_token': user.reset_password_token.to_dict() if user.reset_password_token else None,
            'expired_password_token': user.expired_password_token if user.expired_password_token else None,
            'requested_changes_token': user.requested_changes_token if user.requested_changes_token else None
        }}
    )


def find_users() -> List[User]:
    users: List[User] = []
    for user_data in USERS_COLLECTION.find():
        user = deserialize_user(user_data)
        users.append(user)

    return users


def find_user_by_id(user_id: str):
    user_data = USERS_COLLECTION.find_one({'_id': user_id})
    if user_data:
        return deserialize_user(user_data)


def find_user_by_email(email: str):
    for user_data in USERS_COLLECTION.find():
        if email and user_data.get('email') and email.lower() == utils.decrypt_message(user_data.get('email')).lower():
            return deserialize_user(user_data)


def deserialize_user(user_data: Dict) -> User:
    return User(
        id=user_data.get('_id'),
        email=utils.decrypt_message(user_data.get('email')),
        given_names=utils.decrypt_message(user_data.get('given_names')),
        family_names=utils.decrypt_message(user_data.get('family_names')),
        nickname=utils.decrypt_message(user_data.get('nickname')),
        language=Language[utils.decrypt_message(user_data.get('language'))],
        anti_phishing_phrase=utils.decrypt_message(user_data.get('anti_phishing_phrase')),
        passwords=deserialize_passwords(user_data.get('passwords')),
        creation_date=utils.get_datetime_from_str(utils.decrypt_message(user_data.get('creation_date'))),
        role=UserRole[utils.decrypt_message(user_data.get('role'))],
        state=State[utils.decrypt_message(user_data.get('state'))],
        refresh_tokens=deserialize_refresh_tokens(user_data.get('refresh_tokens')),
        invitations=deserialize_user_invitations(user_data.get('invitations')),
        reset_password_token=deserialize_reset_password(user_data.get('reset_password_token')),
        expired_password_token=user_data.get('expired_password_token') if user_data.get(
            'expired_password_token') else None,
        requested_changes_token=user_data.get('requested_changes_token') if user_data.get(
            'requested_changes_token') else None
    )


def deserialize_user_invitations(user_invitations_data: Dict) -> List[UserInvitation]:
    invitations = []
    if user_invitations_data:
        for invitation_data in user_invitations_data:
            invitations.append(UserInvitation(
                utils.decrypt_message(invitation_data.get('new_user_email')),
                invitation_data.get('validation_code')
            ))

    return invitations


def deserialize_reset_password(reset_password_token_dict: Dict):
    if reset_password_token_dict:
        return ResetPasswordToken(
            token=reset_password_token_dict.get('token'),
            expiration_date=utils.get_datetime_from_str(reset_password_token_dict.get('expiration_date'))
        )

    return None


def deserialize_passwords(passwords: List[Dict]) -> List[UserPassword]:
    passwords_list = []
    for password_data in passwords:
        passwords_list.append(
            UserPassword(
                password='',
                expiration_date=utils.get_datetime_from_str(
                    utils.decrypt_message(password_data.get('expiration_date'))),
                password_attempts=int(utils.decrypt_message(password_data.get('password_attempts'))),
                encrypted_password=password_data.get('encrypted_password'),
                state=State[utils.decrypt_message(password_data.get('state'))]
            )
        )

    return passwords_list


def deserialize_refresh_tokens(refresh_tokens: List[Dict]) -> List[RefreshToken]:
    if refresh_tokens:
        refresh_tokens_list = []
        for refresh_token_data in refresh_tokens:
            refresh_tokens_list.append(
                RefreshToken(
                    token=refresh_token_data.get('token'),
                    source=utils.decrypt_message(refresh_token_data.get('source'))
                )
            )

        return refresh_tokens_list
