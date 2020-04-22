import logging
import os
from enum import Enum

import requests

logger = logging.getLogger("reddit_scraper")


class Status(Enum):
    SUCCESS = ''
    START = '/start'
    FAIL = '/fail'


class HealthCheck:
    HC_UUID = "HC_UUID"

    @staticmethod
    def ping_status(status: Status):
        if "DEV_RUN" in os.environ:
            return
        if HealthCheck.HC_UUID not in os.environ:
            raise EnvironmentError(f"Missing {HealthCheck.HC_UUID=}")
        requests.get(f"https://hc-ping.com/{os.getenv(HealthCheck.HC_UUID)}{status.value}")
