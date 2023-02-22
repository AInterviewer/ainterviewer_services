import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

import services.admin_services as adm_serv
import services.user_services as user_serv
from constants import PROCESS_USERS_CRON
from infra.logs import logging_config

scheduler = BlockingScheduler()


def configure_app():
    logging_config()
    adm_serv.start_app()


if __name__ == "__main__":
    configure_app()
    logging.info('Ready to manage cron tasks...')
    scheduler.add_job(user_serv.check_expired_passwords, CronTrigger.from_crontab(PROCESS_USERS_CRON))

# Starting cron tasks
scheduler.start()
