import logging
import logging.handlers as handlers

from constants import LOG_LEVEL

MATCHES = ['Running job', 'Adding job', 'Added job', 'Scheduler started', 'Job ', 'Execution of job']


class NoRunningFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return not any(x in record.msg for x in MATCHES)


def logging_config():
    # get the root logger
    root_logger = logging.getLogger()
    # set overall level
    root_logger.setLevel(LOG_LEVEL)

    # set log filer
    log_filter = NoRunningFilter()

    # setup logging to file, rotating at midnight
    file_log = logging.handlers.TimedRotatingFileHandler(f'data/logs/tasks.log',
                                                         when='midnight', backupCount=60)
    file_log.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter('[%(asctime)s] - %(levelname)s %(message)s')
    file_log.setFormatter(file_formatter)
    file_log.addFilter(log_filter)
    root_logger.addHandler(file_log)

    # setup logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s %(message)s')
    console.setFormatter(formatter)
    console.addFilter(log_filter)
    root_logger.addHandler(console)
