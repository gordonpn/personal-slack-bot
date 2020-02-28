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
            response = requests.get(url)
            if response.ok:
                content = response.text
                title_match = re.search(r'<\W*title\W*(.*)</title', content, re.IGNORECASE)
                site_title: str = title_match.group(1)
                if self.config.monitor_config.titles[index] in site_title:
                    print(f"{url} is matching")
                    continue
            message: str = f"{url} may be down"
            print(message)
            formatted_messages.append(message)

        return formatted_messages
