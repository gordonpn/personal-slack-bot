import re
from typing import List

import requests

from Configuration.config import get_config
from Configuration.logger import get_logger


class MonitorBot:
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()

    def check_sites(self) -> List[str]:
        urls: List[str] = self.config.monitor_config.monitor_list
        formatted_messages: List[str] = []

        for index, url in enumerate(urls):
            response = requests.head(url)
            if not response.ok:
                message: str = f"{url} may be down"
                print(message)
                formatted_messages.append(message)

        return formatted_messages
