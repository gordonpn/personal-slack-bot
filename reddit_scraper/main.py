import logging
import time
from logging.config import fileConfig

import schedule

from .healthcheck.healthcheck import HealthCheck, Status

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("reddit_scraper")


def job():
    try:
        pass
    except Exception:
        HealthCheck.ping_status(Status.FAIL)
        raise Exception


def start_schedule():
    logger.debug("Setting schedule")
    schedule.every(10).to(20).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    pass
