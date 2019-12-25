from SlackBot.slack_bot import Bot

bots = []


def get_bot(data, web_client):
    global bots

    if bots:
        if len(bots) > 0:
            return bots[0]
        else:
            raise Exception("No bot available for usage")
    else:
        bot = Bot(data, web_client)
        bots.append(bot)
        return bot
