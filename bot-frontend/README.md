# Reddit Scraper Bot Frontend

## Getting started with development

### Setting up ngrok

To make development easier, we can use ngrok on our local machine to make the events endpoint available to Slack.

Start ngrok with using the default port: `ngrok port 3000`.

Go to <https://api.slack.com/apps/A035GE866R3/event-subscriptions> and <https://api.slack.com/apps/A035GE866R3/interactive-messages> to change the request URL to `https://aaaa-111-111-111-111.ngrok.io/slack/events`. (Change the URL to yours).
