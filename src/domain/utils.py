import datetime
import logging
import random
import string
import uuid

from cryptography.fernet import Fernet

from constants import DATE_FORMAT, DATETIME_FORMAT, ENCRYPT_KEY, APP_ENVIRONMENT
from domain.enums import Environment, Language, UserRole, State
from domain.users import User, UserPassword

SPECIAL_SYMBOLS = ['!', '#', '$', '%', '&', '/', '(', ')', '=', '?', '¡', '|', '-', '_', '¿', '[', ']', '{', '}',
                   '^', '<', '>', '.', ',', ';', ':', '+', '*', '~', '@']


def get_datetime_from_str(datetime_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(datetime_str, DATETIME_FORMAT)


def get_today_str():
    return datetime.datetime.utcnow().date().strftime(DATE_FORMAT)


def get_now_str():
    return datetime.datetime.utcnow().strftime(DATETIME_FORMAT)


def encrypt_message(message: str):
    if APP_ENVIRONMENT != Environment.PROD.name:
        return message

    key = ENCRYPT_KEY.encode()
    return Fernet(key).encrypt(message.encode())


def decrypt_message(encrypted_message: bytes):
    if APP_ENVIRONMENT != Environment.PROD.name:
        return encrypted_message

    key = ENCRYPT_KEY.encode()
    return Fernet(key).decrypt(encrypted_message).decode()


def is_valid_password(password: str) -> bool:
    if APP_ENVIRONMENT == Environment.DEV.name or APP_ENVIRONMENT == Environment.STAGE.name:
        return len(password) > 0

    return (len(password) > 7
            and any(char.isdigit() for char in password)
            and any(char.isupper() for char in password)
            and any(char.islower() for char in password)
            and any(char in SPECIAL_SYMBOLS for char in password))


def get_random_string(length):
    return ''.join(random.choice(string.hexdigits) for _ in range(length))


def create_admin() -> User:
    password = get_random_string(20)
    logging.warning(f'Admin password is {password} '
                    f'Remember change this password and the secure phrase as soon as you see this message. '
                    f'Do not store them in any insecure place.')

    user = User(id=str(uuid.uuid4()),
                email='adm' if APP_ENVIRONMENT == Environment.DEV.name else 'support@ainterviewer.tech',
                given_names='Admin',
                family_names='AInterviewer',
                nickname='Admin',
                language=Language.SPANISH,
                passwords=[UserPassword(password=password)],
                role=UserRole.ADMIN,
                state=State.ACTIVE,
                anti_phishing_phrase='Phrase to change')

    return user
