import datetime

import infra.email_manager as email
import infra.email_subjects as subjects
from constants import DATE_FORMAT
from domain.enums import Language
from domain.users import User, UserInvitation


def send_invitation(user: User, new_user_email: str, new_invitation: UserInvitation,
                    invitation_language: Language):
    subject = subjects.get_subject(language=invitation_language, notification='invitation')
    email.send_message(
        locale=invitation_language,
        template='invitation',
        to=new_user_email,
        subject=subject,
        user_given_names=user.given_names,
        user_family_names=user.family_names,
        new_user_email=new_user_email,
        user_id=user.id,
        new_invitation_validation_code=new_invitation.validation_code
    )


def send_created_account(user: User, user_created: User):
    subject = subjects.get_subject(
        language=user.language, notification='created_account'
    )

    email.send_message(
        locale=user.language,
        template='created_account',
        to=user.email,
        subject=subject,
        anti_phishing_phrase=user.anti_phishing_phrase,
        user_nickname=user.nickname,
        new_user_email=user_created.email
    )


def send_activated_account(user: User):
    subject = subjects.get_subject(
        language=user.language, notification='activated_account',
        user_nickname=user.nickname
    )

    email.send_message(
        locale=user.language,
        template='activated_account',
        to=user.email,
        subject=subject,
        anti_phishing_phrase=user.anti_phishing_phrase,
        user_nickname=user.nickname,
        user_email=user.email
    )


def send_reactivated_account(user: User):
    subject = subjects.get_subject(
        language=user.language, notification='reactivated_account',
        user_nickname=user.nickname
    )

    email.send_message(
        locale=user.language,
        template='reactivated_account',
        to=user.email,
        subject=subject,
        anti_phishing_phrase=user.anti_phishing_phrase,
        user_nickname=user.nickname,
        user_id=user.id,
        user_reset_password_token_token=user.reset_password_token.token
    )


def send_forgot_password(user: User, expiration_minutes: int):
    subject = subjects.get_subject(
        language=user.language, notification='forgot_password'
    )

    email.send_message(
        locale=user.language,
        template='forgot_password',
        to=user.email,
        subject=subject,
        anti_phishing_phrase=user.anti_phishing_phrase,
        user_nickname=user.nickname,
        user_id=user.id,
        user_reset_password_token_token=user.reset_password_token.token,
        expiration_minutes=expiration_minutes
    )


def send_changed_password(user: User, source: str):
    subject = subjects.get_subject(
        language=user.language, notification='changed_password'
    )

    email.send_message(
        locale=user.language,
        template='changed_password',
        to=user.email,
        subject=subject,
        anti_phishing_phrase=user.anti_phishing_phrase,
        user_nickname=user.nickname,
        datetime=datetime.datetime.now().strftime(DATE_FORMAT),
        source=source,
        user_id=user.id,
        user_reset_password_token_token=user.reset_password_token.token
    )


def send_password_expired(user: User):
    subject = subjects.get_subject(
        language=user.language, notification='password_expired'
    )

    email.send_message(
        locale=user.language,
        template='password_expired',
        to=user.email,
        subject=subject,
        anti_phishing_phrase=user.anti_phishing_phrase,
        user_nickname=user.nickname,
        user_id=user.id,
        user_expired_password_token=user.expired_password_token
    )


def send_password_near_to_expire(user: User, days_to_expire: int):
    subject = subjects.get_subject(
        language=user.language, notification='password_near_to_expire'
    )

    email.send_message(
        locale=user.language,
        template='password_near_to_expire',
        to=user.email,
        subject=subject,
        anti_phishing_phrase=user.anti_phishing_phrase,
        user_nickname=user.nickname,
        days_to_expire=days_to_expire
    )


def send_message_to_user(user: User, message: str, subject: str):
    email.send_message(
        locale=user.language,
        template='message_to_user',
        to=user.email,
        subject=subject,
        anti_phishing_phrase=user.anti_phishing_phrase,
        message=message
    )
