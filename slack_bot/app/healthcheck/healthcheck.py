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
        if "SLACK_HC_UUID" not in os.environ:
            raise EnvironmentError("Missing SLACK_HC_UUID")
        requests.get(f"https://hc-ping.com/{os.getenv('SLACK_HC_UUID')}{status.value}")
