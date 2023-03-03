import os
from typing import Any


def env(key: str, default: Any) -> str:
    return os.environ.get(key, default)


def to_bool(expr: Any) -> bool:
    return str(expr) == 'True'


# Security constants
PASSWORD_DAYS_TO_EXPIRATION = 60
REMAINING_PASSWORD_DAYS_TO_SEND_NOTIFICATION = 5
MAXIMUM_WRONG_PASSWORD_ATTEMPTS = 3
SECURITY_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 60
CHANGE_PASSWORD_TOKEN_EXPIRE_MINUTES = 15
REACTIVATED_USER_TOKEN_EXPIRE_DAYS = 30

# Error codes
USER_NOT_FOUND = 'user-not-found'
NOT_VALID_CREDENTIALS = 'not-valid-credentials'
USER_INACTIVATED_FOR_MAX_ATTEMPTS = 'user-inactivated-for-max-attempts'
INVALID_CREDENTIALS = 'invalid-credentials'
INACTIVE_USER = 'inactive-user'
PASSWORDS_DO_NOT_MATCH = 'passwords-do-not-match'
PASSWORDS_ALREADY_USED = 'password-already-used'
NOT_ALLOWED_TO_CHANGE_PASSWORD = 'not-allowed-to-change-password'
INVALID_RESET_PASSWORD_TOKEN = 'invalid-reset-password-token'
INVALID_EXPIRED_PASSWORD_TOKEN = 'invalid-expired-password-token'
INVALID_REQUEST_CHANGES_TOKEN = 'invalid-request-changes-token'
USER_NOT_AUTHENTICATED = 'user-not-authenticated'
USER_ALREADY_EXIST_WITH_USERNAME = 'user-already-exist-with-username'
USER_ALREADY_EXIST_WITH_EMAIL = 'user-already-exist-with-email'
SPONSOR_NOT_FOUND = 'sponsor-not-found'
INVALID_INVITATION = 'invalid-invitation'
INVITATION_ALREADY_USED = 'invitation-already-used'
PROJECT_ALREADY_EXIST = 'project-already-exist'
PROJECT_DO_NOT_EXIST = 'project-do-not-exist'
USER_NOT_IN_PROJECT = 'user-not-in-project'
EVALUATION_DO_NOT_EXIST = 'evaluation-do-not-exist'
QUESTION_DO_NOT_EXIST = 'question-do-not-exist'

# date time formats
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'

# For PROD, STAGE, DEV environments
APP_ENVIRONMENT = env('APP_ENVIRONMENT', 'DEV')

# Log level
LOG_LEVEL = env('LOG_LEVEL', 'INFO')

# Web UI path
WEB_UI_PATH = env('WEB_UI_PATH', 'http://localhost:3000')

# Encryption key
ENCRYPT_KEY = env('ENCRYPT_KEY', 'gM50WkuSrEO1ZfPKEobIK1GPvf6uSKAkKZOPJtWhddU=')

# Mongo string
MONGO_CONNECTION = env('MONGO_CONNECTION', 'mongodb://admin:admin@localhost:27017')

# API
API_PORT = int(env('API_PORT', 8000))
API_RELOAD = to_bool(env('API_RELOAD', True))

# Cron
PROCESS_USERS_CRON = env('PROCESS_USERS_CRON', '*/1 * * * *')

# Email Server
SMTP_PORT = int(env('SMTP_PORT', 0))
SMTP_SERVER = env('SMTP_SERVER', '')
SENDER_EMAIL = env('SENDER_EMAIL', '')
SENDER_PASSWORD = env('SENDER_PASSWORD', '')

# Open API
MODEL = env('MODEL', 'gpt-3.5-turbo')
MAX_TOKENS = int(env('MAX_TOKENS', 32))
MODEL_TEMPERATURE = float(env('MODEL_TEMPERATURE', 0.5))
API_KEY = env('API_KEY', '')
QUESTION_EN = env('QUESTION_EN', 'Write the next question but in different words "<topic>"')
QUESTION_ES = env('QUESTION_ES', 'Escribe la siguiente pregunta pero con palabras diferentes "<topic>"')
ANSWERS = env('ANSWERS', 'For the question "<question>" could you evaluate from 1 to 5 being 1 is not good '
                         'and 5 is an excellent response: "<answer>". Give me the response'
                         ' in format: "(integer), (a short explanation of the number given in the same '
                         'language of the question)"')
