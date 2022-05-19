import { AppHomeOpenedEvent, Logger } from "@slack/bolt";
import {
  PlainTextElement,
  PlainTextOption,
  ViewsPublishArguments,
  WebClient,
} from "@slack/web-api";
import { Action } from "./actions";

const fetchSubscribedSubreddits = () => {
  // TODO fetch subreddits from another service
  return ["value_0", "value_1", "value_2", "value_3", "value_4", "value_5"];
};

const getPlainTextElement = (value: string): PlainTextElement => {
  return {
    type: "plain_text",
    text: value,
  };
};

const subscribedSubreddits = () => {
  const subreddits = fetchSubscribedSubreddits();
  const subscriptions: PlainTextElement[] = [];

  subreddits.forEach((value) => {
    const aSubscription: PlainTextElement = getPlainTextElement(value);
    subscriptions.push(aSubscription);
  });

  return subscriptions;
};

const subredditOptions = () => {
  const subreddits = fetchSubscribedSubreddits();
  const options: PlainTextOption[] = [];

  subreddits.forEach((value) => {
    const anOption: PlainTextOption = {
      text: getPlainTextElement(value),
      value: value,
    };
    options.push(anOption);
  });

  return options;
};

export const getView = (userId: string): ViewsPublishArguments => {
  return {
    // Use the user ID associated with the event
    user_id: userId,
    view: {
      type: "home",
      blocks: [
        {
          type: "header",
          text: {
            type: "plain_text",
            text: "Reddit Scraper Bot",
            emoji: true,
          },
        },
        {
          type: "divider",
        },
        {
          type: "section",
          text: {
            type: "plain_text",
            text: "You are currently subscribed to the following subreddits:",
          },
          fields: subscribedSubreddits(),
        },
        {
          type: "divider",
        },
        {
          type: "input",
          element: {
            type: "plain_text_input",
            action_id: Action.Subscribe,
            placeholder: {
              type: "plain_text",
              text: "Enter a subreddit",
            },
          },
          dispatch_action: true,
          label: {
            type: "plain_text",
            text: "Subscribe to a new subreddit",
            emoji: true,
          },
        },
        {
          type: "divider",
        },
        {
          type: "header",
          text: {
            type: "plain_text",
            text: "Unsubscribe from a subreddit",
          },
        },
        {
          type: "actions",
          block_id: "unsubscribeBlock",
          elements: [
            {
              type: "static_select",
              placeholder: {
                type: "plain_text",
                text: "Select a subreddit",
              },
              action_id: Action.UnsubscribeSelect,
              options: subredditOptions(),
            },
            {
              type: "button",
              text: {
                type: "plain_text",
                text: "Unsubscribe",
              },
              value: "Unsubscribe",
              style: "danger",
              action_id: Action.Unsubscribe,
            },
          ],
        },
      ],
    },
  };
};

export const appHomeHandler = async ({
  event,
  client,
  logger,
}: {
  event: AppHomeOpenedEvent;
  client: WebClient;
  logger: Logger;
}) => {
  try {
    // Call views.publish with the built-in client
    const result = await client.views.publish(getView(event.user));

    logger.info(result);
    logger.debug(event.user);
  } catch (error) {
    logger.error(error);
  }
};
