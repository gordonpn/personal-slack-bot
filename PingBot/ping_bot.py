import concurrent.futures
import os
import subprocess
import time
from typing import Dict, List, Set

from Configuration.config import get_config
from Configuration.logger import get_logger


class PingBot:
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()

    def parse_message(self, message_received: str) -> str:
        message = "Unrecognized command, the syntax is: ping [watch (optional)] [name or all]"
        is_member: List[str] = self.is_member(message_received)

        if 'watch' in message_received:
            message = self.set_watch(is_member)
        elif 'all' in message_received:
            message = self.ping_devices()
        elif is_member:
            message = self.ping_devices(is_member)

        return message

    def format_message(self, active: Dict[str, str]) -> str:
        if active:
            message: str = ""
            for name, ip in active.items():
                devices: str = f"{name} ({ip})"
                message += f"{devices}, "
            message += "responded"
        else:
            self.logger.debug("Nothing passed in parameters for format message")
            message: str = "None of the devices responded"
        return message

    def is_member(self, message: str) -> List[str]:
        message_received_as_list: List[str] = self.clean_message(message.split())

        set_from_config = set(self.config.ping_config.friendly_name)
        set_from_message = set(message_received_as_list)

        intersection: Set[str] = set_from_config.intersection(set_from_message)

        if intersection:
            return list(intersection)
        return []

    def clean_message(self, message: List[str]) -> List[str]:
        self.logger.debug("Sanitizing string for further processing")
        return [value for value in message if value != 'ping' or value != 'watch' or value != 'all']

    def ping_devices(self, message: List[str] = None) -> str:
        ping_dict: Dict[str, str] = {}
        friendly_name_list: List[str] = self.config.ping_config.friendly_name
        ip_list: List[str] = self.config.ping_config.addresses
        if message:
            for name in message:
                index: int = friendly_name_list.index(name)
                ping_dict[name] = ip_list[index]
            self.logger.debug("Attempting to ping a subset of addresses")
        else:
            ping_dict = dict(zip(friendly_name_list, ip_list))
            self.logger.debug("Attempting to ping all addresses")
        active: Dict[str, str] = {}
        with open(os.devnull, 'wb') as limbo:
            for name, ip in ping_dict.items():
                result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "5", ip], stdout=limbo, stderr=limbo).wait()
                if result == 0:
                    active[name] = ip

        return self.format_message(active)

    def set_watch(self, message: List[str] = None) -> str:
        if not message:
            message: List[str] = self.config.ping_config.friendly_name
        for name in message:
            self.logger.debug(f"Setting ping watch for {name}")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.watch_helper, name)
                return future.result()

    def watch_helper(self, who: str) -> str:
        ping_list: List[str] = [who]
        successful_ping: bool = False
        while not successful_ping:
            message: str = self.ping_devices(ping_list)
            if not message.startswith('None'):
                self.logger.debug(f"Successfully pinged {who}")
                return message
            self.logger.debug("Retrying ping in 10 seconds")
            time.sleep(10)
