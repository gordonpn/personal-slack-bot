import logging
import time
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
        HealthCheck.ping_status(Status.FAIL)
        raise Exception
    HealthCheck.ping_status(Status.SUCCESS)


def start_schedule():
    logger.debug("Setting schedule")
    schedule.every(10).to(20).minutes.do(job)

    while True:
        logger.debug("Pending scheduled job")
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    start_schedule()
