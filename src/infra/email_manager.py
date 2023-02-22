import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import join, exists, getmtime

from jinja2 import Environment, select_autoescape, BaseLoader, TemplateNotFound

import domain.enums as enums
from constants import SMTP_PORT, SMTP_SERVER, SENDER_EMAIL, SENDER_PASSWORD, APP_ENVIRONMENT, WEB_UI_PATH


class EmailTemplatesLoader(BaseLoader):
    def __init__(self, path):
        self.path = path

    def get_source(self, environment, template):
        path = join(self.path, template)
        if not exists(path):
            raise TemplateNotFound(template)
        mtime = getmtime(path)
        with open(path) as f:
            source = f.read()
        return source, path, lambda: mtime == getmtime(path)


env = Environment(
    loader=EmailTemplatesLoader('data/email_templates'),
    autoescape=select_autoescape()
)


def send_message(locale: enums.Language, template: str, to: str, subject: str, **kwargs):
    try:
        template = env.get_template(f'{locale.value}/{template}.html')
        send_email(to, subject, template.render(WEB_UI_PATH=WEB_UI_PATH, **kwargs))
    except Exception as e:
        logging.error(f'Error sending email to={to}, subject={subject}, template={template.name}\n{e}', exc_info=True)


def send_email(to: str, subject: str, content: str):
    logging.info(f'Sent email to: {to}, subject: {subject}')
    if APP_ENVIRONMENT != enums.Environment.PROD.name:
        send_fake_email(content)
        return

    mime = MIMEText(content, 'html')
    message = MIMEMultipart('alternative')
    message.attach(mime)
    message['Subject'] = subject
    message['From'] = SENDER_EMAIL
    message['To'] = to

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to, message.as_string())
        server.close()


def send_fake_email(content: str):
    logging.info(f'content:\n{content}')
