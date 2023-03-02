import datetime
from dataclasses import dataclass
from typing import Optional, List

import bcrypt

from constants import DATETIME_FORMAT, PASSWORD_DAYS_TO_EXPIRATION
from domain import utils
from domain.enums import State, Language, UserRole


@dataclass
class UserInvitation:
    new_user_email: str
    validation_code: str

    def to_dict(self):
        return {
            'new_user_email': utils.encrypt_message(self.new_user_email),
            'validation_code': self.validation_code
        }


@dataclass
class ResetPasswordToken:
    token: str
    expiration_date: datetime.datetime

    def to_dict(self):
        return {
            'token': self.token,
            'expiration_date': self.expiration_date.strftime(DATETIME_FORMAT)
        }


@dataclass
class RefreshToken:
    token: str
    source: str

    def to_dict(self):
        return {
            'token': self.token,
            'source': utils.encrypt_message(self.source)
        }


@dataclass
class UserPassword:
    password: str
    password_attempts: int = 0
    expiration_date: Optional[datetime.datetime] = None
    encrypted_password: Optional[bytes] = None
    state: State = State.ACTIVE

    def __post_init__(self):
        if self.password:
            self.encrypted_password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt())
            self.expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=PASSWORD_DAYS_TO_EXPIRATION)

    def to_dict(self):
        return {
            'password_attempts': utils.encrypt_message(str(self.password_attempts)),
            'encrypted_password': self.encrypted_password,
            'expiration_date': utils.encrypt_message(self.expiration_date.strftime(DATETIME_FORMAT)),
            'state': utils.encrypt_message(self.state.name)
        }


@dataclass
class User:
    id: str
    email: str
    given_names: str
    family_names: str
    nickname: str
    language: Language
    role: UserRole
    passwords: List[UserPassword]
    anti_phishing_phrase: str
    creation_date: datetime.datetime = datetime.datetime.utcnow()
    state: State = State.INACTIVE
    refresh_tokens: Optional[List[RefreshToken]] = None
    invitations: Optional[List[UserInvitation]] = None
    reset_password_token: Optional[ResetPasswordToken] = None
    expired_password_token: Optional[str] = None
    requested_changes_token: Optional[str] = None
    projects: Optional[List[str]] = None

    def get_current_active_password(self):
        active_passwords = [password for password in self.passwords if password.state == State.ACTIVE]
        if active_passwords and active_passwords[0]:
            return active_passwords[0]

    def verify_password(self, password_to_validate: str):
        password = self.get_current_active_password()
        if password:
            return bcrypt.checkpw(password_to_validate.encode(), password.encrypted_password)

    def add_refresh_token(self, encoded_jwt, source):
        new_token = RefreshToken(encoded_jwt, source)
        if not self.refresh_tokens:
            self.refresh_tokens = []

        self.refresh_tokens.append(new_token)

    def already_used_password(self, new_password):
        for password in self.passwords:
            if bcrypt.checkpw(new_password.encode(), password.encrypted_password):
                return True

        return False

    def update_password(self, new_password: str):
        password = self.get_current_active_password()
        if password:
            password.state = State.INACTIVE

        self.passwords.append(UserPassword(password=new_password))

    def inactivate_user(self):
        self.refresh_tokens = None
        self.reset_password_token = None
        self.expired_password_token = None
        self.state = State.INACTIVE
        password = self.get_current_active_password()
        password.state = State.INACTIVE

    def to_dict(self) -> dict:
        return {
            '_id': self.id,
            'email': utils.encrypt_message(self.email),
            'given_names': utils.encrypt_message(self.given_names),
            'family_names': utils.encrypt_message(self.family_names),
            'nickname': utils.encrypt_message(self.nickname),
            'language': utils.encrypt_message(self.language.name),
            'anti_phishing_phrase': utils.encrypt_message(self.anti_phishing_phrase),
            'role': utils.encrypt_message(self.role.name),
            'state': utils.encrypt_message(self.state.name),
            'creation_date': utils.encrypt_message(self.creation_date.strftime(DATETIME_FORMAT)),
            'passwords': [password.to_dict() for password in self.passwords],
            'refresh_tokens': [refresh_token.to_dict() for refresh_token in
                               self.refresh_tokens] if self.refresh_tokens else None,
            'invitations': [invitation.to_dict() for invitation in self.invitations] if self.invitations else None,
            'reset_password_token': self.reset_password_token.to_dict() if self.reset_password_token else None,
            'expired_password_token': utils.encrypt_message(
                self.expired_password_token) if self.expired_password_token else None,
            'requested_changes_token': utils.encrypt_message(
                self.requested_changes_token) if self.requested_changes_token else None,
            'projects': self.projects
        }

    def to_api_response(self):
        return {
            'id': self.id,
            'email': self.email,
            'given_names': self.given_names,
            'family_names': self.family_names,
            'nickname': self.nickname,
            'language': self.language,
            'anti_phishing_phrase': self.anti_phishing_phrase,
            'role': self.role.name,
            'state': self.state.name,
            'creation_date': self.creation_date.strftime(DATETIME_FORMAT),
            'projects': self.projects
        }

    def to_simple_data(self):
        return {
            'id': self.id,
            'email': self.email,
            'given_names': self.given_names,
            'family_names': self.family_names,
            'nickname': self.nickname,
        }
