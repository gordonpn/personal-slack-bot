import logging
import os
from enum import Enum

import requests

logger = logging.getLogger("reddit_scraper")


class Status(Enum):
    SUCCESS = ""
    START = "/start"
    FAIL = "/fail"


class HealthCheck:
    @staticmethod
    def ping_status(status: Status):
        if "DEV_RUN" in os.environ:
            return
        if "SCRAPER_HC_UUID" not in os.environ:
            raise EnvironmentError("Missing SCRAPER_HC_UUID")
        requests.get(
            f"https://hc-ping.com/{os.getenv('SCRAPER_HC_UUID')}{status.value}"
        )
