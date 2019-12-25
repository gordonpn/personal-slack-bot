from Configuration.config import get_config


class Pinger:
    def __init__(self):
        self.config = get_config()

    def parse_message(self, message_received: str) -> str:
        pass
