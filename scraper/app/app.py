import logging
import time
import os
from logging.config import fileConfig

import schedule

from .scraper.scraper import RedditScraper
from .healthcheck.healthcheck import HealthCheck, Status

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("reddit_scraper")


def job():
    HealthCheck.ping_status(Status.START)
    try:
        scraper = RedditScraper()
        scraper.run()
    except Exception:
        raise Exception
    HealthCheck.ping_status(Status.SUCCESS)


def start_schedule():
    logger.debug("Setting schedule")
    job()
    if "DEV_RUN" not in os.environ:
        schedule.every(10).to(20).minutes.do(job)

    logger.debug("Pending scheduled job")
    while True:
        schedule.run_pending()
        time.sleep(3 * 60)


def run():
    start_schedule()
