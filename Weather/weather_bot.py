import time
from typing import Tuple

import requests

from Configuration.config import get_config
from Configuration.logger import get_logger


class WeatherBot:
    ONE_DAY: int = 86400;
    DEGREES_SIGN = u'\N{DEGREE SIGN}'

    def __init__(self):
        self.config = get_config()
        # self.config = get_config('../bot.conf')
        self.logger = get_logger()

    def parse_message(self, message_received: str) -> str:
        message = "Unrecognized command, the syntax is: weather ['today' or 'tomorrow' or 'after tomorrow']"
        today: time = int(time.time())

        if 'today' in message_received:
            yesterday: time = today - WeatherBot.ONE_DAY
            data: Tuple[bool, float] = self.is_warmer_than(today, yesterday)
            precip: Tuple[int, str] = self.precip_forecast(today)
            if data[0]:
                message = f"Today is warmer compared to yesterday by {data[1]}{WeatherBot.DEGREES_SIGN}."
            else:
                message = f"Yesterday was warmer compared to today by {data[1]}{WeatherBot.DEGREES_SIGN}."
            message = message + f"\nWith {precip[0]}% chance of {precip[1]} today."
        elif 'after tomorrow' in message_received:
            after_tomorrow: time = today + 2 * WeatherBot.ONE_DAY
            data: Tuple[bool, float] = self.is_warmer_than(today, after_tomorrow)
            precip: Tuple[int, str] = self.precip_forecast(after_tomorrow)
            if data[0]:
                message = f"Today will be warmer than the day after tomorrow by {data[1]}{WeatherBot.DEGREES_SIGN}."
            else:
                message = f"The day after tomorrow will be warmer than today by {data[1]}{WeatherBot.DEGREES_SIGN}."
            message = message + f"\nWith {precip[0]}% chance of {precip[1]} the day after tomorrow."
        elif 'tomorrow' in message_received:
            tomorrow: time = today + WeatherBot.ONE_DAY
            data: Tuple[bool, float] = self.is_warmer_than(today, tomorrow)
            precip: Tuple[int, str] = self.precip_forecast(tomorrow)
            if data[0]:
                message = f"Today will be warmer than tomorrow by {data[1]}{WeatherBot.DEGREES_SIGN}."
            else:
                message = f"Tomorrow will be warmer than today by {data[1]}{WeatherBot.DEGREES_SIGN}"
            message = message + f"\nWith {precip[0]}% chance of {precip[1]} tomorrow."

        return message

    def is_warmer_than(self, this_time, that_time) -> Tuple[bool, float]:
        this_json: Dict[str, object] = requests.get(url=self.get_url(this_time)).json()
        that_json: Dict[str, object] = requests.get(url=self.get_url(that_time)).json()
        this_data: Dict[str, object] = this_json.get('daily').get('data')[0]
        that_data: Dict[str, object] = that_json.get('daily').get('data')[0]
        this_average: float = (this_data.get('apparentTemperatureHigh') + this_data.get('apparentTemperatureLow')) / 2
        that_average: float = (that_data.get('apparentTemperatureHigh') + that_data.get('apparentTemperatureLow')) / 2

        return this_average > that_average, round(abs(this_average - that_average))

    def precip_forecast(self, unix_time) -> Tuple[int, str]:
        precip_json: Dict[str, object] = requests.get(url=self.get_url(unix_time)).json()
        precip_data: Dict[str, object] = precip_json.get('daily').get('data')[0]

        probability: int = int(precip_data.get('precipProbability') * 100)
        precip_type: str = precip_data.get('precipType')

        return probability, precip_type

    def get_url(self, unix_time) -> str:
        return f"https://api.darksky.net/forecast/{self.config.darksky_config.key}/{self.config.darksky_config.location},{unix_time}?units=ca&exclude=currently,minutely,hourly,alerts,flags"
