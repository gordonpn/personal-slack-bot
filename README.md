# Personal Slack bot

## Description

Initially I simply wanted a quick way to ping devices on my home local network from wherever I was.

Later, I realized how useful a Slack bot could be and started developing more features for this personal Slack bot.

---
![GitHub](https://img.shields.io/github/license/gpnn/personal-slack-bot)

![GitHub top language](https://img.shields.io/github/languages/top/gpnn/personal-slack-bot)
![GitHub language count](https://img.shields.io/github/languages/count/gpnn/personal-slack-bot)

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/gpnn/personal-slack-bot)
![GitHub last commit](https://img.shields.io/github/last-commit/gpnn/personal-slack-bot)

## Features

*  Tell the uptime of the server it's currently running on
*  Tell the average CPU load
*  Send unread top posts from favorite Reddit subreddits
*  Notify user of a website being down

## Prerequisites
````bash
pip install -r requirements.txt
````

## Set up

Create a `bot.conf` file as such:
```
[slack]
token =
bot_id =
bot_channel =
user_id =
[ping]
friendly_name =
addresses =
[jenkins]
username =
password =
server_url =
job_url =
[reddit]
client_id =
client_secret =
password =
user_agent =
username =
subreddits =
watchlist =
[darksky]
key =
location =
[monitor]
monitor_list =
titles =
```
All configurations are optional, depends on which features you want to use.

## Usage

The slack bot main starts in `bot.py` where it makes a connection with the Slack API and starts watching for commands from the user. If you'd like to scrape top Reddit posts, then the `reddit_bot.py` must be automated (with Jenkins for example).

To use the site watch feature, you need to provide the web page title that the bot should be expecting (or part of the title) in the `titles` options in the config in the same order as you listed the sites to monitor in `monitor_list`.

## Roadmap/Todo

* [x]  Rewrite in Python
* [x]  Develop a Slack Bot to communicate the information
* [x]  Info on uptime
* [x]  Info on cpu load
* [x]  Refactor code to make more object-oriented
* [x]  watch all addresses feature
* [x]  load from external sources for addresses and jenkins url
* [ ]  stop all threads or stop one thread
* [x]  refactor for better code maintainability
* [x]  integrate personalized weather forecasting
* [x]  return Reddit news on demand only, instead of periodically
* [x]  Website monitoring feature

## License

[MIT License](https://choosealicense.com/licenses/mit/#)
