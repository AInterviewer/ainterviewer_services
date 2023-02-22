from pydantic import BaseModel, EmailStr, validator

from domain import utils
from domain.enums import Language, UserRole

INVALID_PASSWORD = 'Invalid password'


class InviteUserRequest(BaseModel):
    new_user_email: str
    invitation_language: Language

    def to_audit(self):
        return {
            'new_user_email': self.new_user_email,
            'invitation_language': self.invitation_language.name
        }


class CreateUserRequest(BaseModel):
    email: EmailStr
    given_names: str
    family_names: str
    nickname: str
    language: Language
    password: str
    sponsor_user_id: str
    invitation_code: str
    anti_phishing_phrase: str
    user_role: UserRole

    @validator('password')
    def valid_password(cls, value):
        if not utils.is_valid_password(value):
            raise ValueError(INVALID_PASSWORD)
        return value

    def to_audit(self):
        return {
            'email': self.email,
            'given_names': self.given_names,
            'family_names': self.family_names,
            'nickname': self.nickname,
            'language': self.language.name,
            'sponsor_user_id': self.sponsor_user_id,
            'invitation_code': self.invitation_code,
            'anti_phishing_phrase': self.anti_phishing_phrase,
            'user_role': self.user_role.value
        }


class UpdateUserContactInfoRequest(BaseModel):
    nickname: str
    anti_phishing_phrase: str

    def to_audit(self):
        return {
            'nickname': self.nickname,
            'anti_phishing_phrase': self.anti_phishing_phrase
        }


class ApplyChangesRequest(BaseModel):
    user_id: str
    token: str
    given_names: str
    family_names: str
    language: Language

    def to_audit(self):
        return {
            'user_id': self.user_id,
            'token': self.token,
            'language': self.language.name,
        }


class ForgotPasswordRequest(BaseModel):
    email: str


class ChangePasswordRequest(BaseModel):
    password: str
    new_password: str

    @validator('new_password')
    def valid_new_password(cls, value):
        if not utils.is_valid_password(value):
            raise ValueError('Invalid new password')
        return value


class ResetPasswordRequest(BaseModel):
    user_id: str
    new_password: str
    reset_password_token: str

    @validator('new_password')
    def valid_password(cls, value):
        if not utils.is_valid_password(value):
            raise ValueError(INVALID_PASSWORD)
        return value


class ReassignExpiredPasswordRequest(BaseModel):
    user_id: str
    password: str
    expired_password_token: str

    @validator('password')
    def valid_password(cls, value):
        if not utils.is_valid_password(value):
            raise ValueError(INVALID_PASSWORD)
        return value


class SendMessageToUserRequest(BaseModel):
    user_id: str
    message: str
    subject: str

    def to_audit(self):
        return {
            'user_id': self.user_id,
            'message': self.message,
            'subject': self.subject,
        }


class SendMessageToAllUsersRequest(BaseModel):
    message: str
    subject: str
    language: Language

    def to_audit(self):
        return {
            'message': self.message,
            'subject': self.subject,
            'language': self.language.name
        }
