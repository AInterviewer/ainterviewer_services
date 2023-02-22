from domain.enums import Language

SUBJECT = {
    'english': {
        'invitation': 'Welcome to AInterviewer',
        'created_account': 'Created new account',
        'activated_account': '{{user_nickname}}, your account has been activated',
        'reactivated_account': '{{user_nickname}}, your account has been reactivated',
        'forgot_password': 'Change password',
        'changed_password': 'Your password has changed',
        'password_expired': 'Expired password',
        'password_near_to_expire': 'Password near to expire'
    },
    'spanish': {
        'invitation': 'Bienvenid@ a AInterviewer',
        'created_account': 'Creada nueva cuenta',
        'activated_account': '{{user_nickname}}, tu cuenta a sido activada',
        'reactivated_account': '{{user_nickname}}, tu cuenta a sido reactivada',
        'forgot_password': 'Cambiar contraseña',
        'changed_password': 'Tu contraseña ha cambiado',
        'password_expired': 'Contraseña vencida',
        'password_near_to_expire': 'Contraseña cerca de vencerse',
    }
}


def get_subject(language: Language, notification: str, **kwargs) -> str:
    subject = SUBJECT.get(language.value).get(notification)

    for key, value in kwargs.items():
        subject = subject.replace('{{' + key + '}}', value)

    return subject
