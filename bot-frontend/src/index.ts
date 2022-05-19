/* eslint-disable no-console */
/* eslint-disable import/no-internal-modules */
import { App, LogLevel } from "@slack/bolt";
import { Action } from "./handlers/actions";
import { appHomeHandler } from "./handlers/app-home";
import { subscribe } from "./handlers/subscribe";
import { unsubscribeCallbacks } from "./handlers/unsubscribe";
import "./utils/env";

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  logLevel:
    process.env.NODE_ENV === "production" ? LogLevel.INFO : LogLevel.DEBUG,
});

app.use(async ({ next }) => {
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  await next();
});

app.action(Action.Subscribe, subscribe);

const { unsubscribeClicked, unsubscribeSelected } = unsubscribeCallbacks();

app.action(Action.UnsubscribeSelect, unsubscribeSelected);

app.action(Action.Unsubscribe, unsubscribeClicked);

app.event("app_home_opened", appHomeHandler);

(async () => {
  const port = Number(process.env.PORT) || 3000;
  await app.start(port);

  console.log(`Bolt app started on port : ${port}`);
})();
