from Configuration.config import get_config


class JenkinsBot:
    def __init__(self):
        self.config = get_config()

    def parse_message(self, message_received: str) -> str:
        message = "Unrecognized command, the syntax is: jenkins"

        return message
