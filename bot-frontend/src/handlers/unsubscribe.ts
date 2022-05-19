import {
  AckFn,
  BlockElementAction,
  DialogSubmitAction,
  DialogValidation,
  InteractiveAction,
  Logger,
  SayArguments,
  SlackAction,
  StaticSelectAction,
  WorkflowStepEdit,
} from "@slack/bolt";
import { WebClient } from "@slack/web-api";
import { Action } from "./actions";
import { getView } from "./app-home";

export function unsubscribeCallbacks() {
  // TODO maybe use Redis, to keep this temporary value in memory
  let selectedSubreddit: string | null = null;

  async function unsubscribeSelected({
    ack,
    logger,
    payload,
  }: {
    ack: AckFn<void> | AckFn<string | SayArguments> | AckFn<DialogValidation>;
    logger: Logger;
    payload:
      | DialogSubmitAction
      | WorkflowStepEdit
      | BlockElementAction
      | InteractiveAction;
  }) {
    logger.debug(`${Action.UnsubscribeSelect} clicked`);
    const selectedValue = (payload as StaticSelectAction).selected_option.value;
    logger.debug(`User selected: ${selectedValue}`);
    selectedSubreddit = selectedValue;
    await ack();
  }

  async function unsubscribeClicked({
    ack,
    logger,
    body,
    client,
  }: {
    ack: AckFn<void> | AckFn<DialogValidation> | AckFn<string | SayArguments>;
    logger: Logger;
    body: SlackAction;
    client: WebClient;
  }) {
    logger.debug(`${Action.Unsubscribe} clicked`);
    logger.debug(`Will unsubscribe from ${selectedSubreddit}`);
    selectedSubreddit = null;
    // TODO force update view?
    client.views.publish(getView(body.user.id));

    await ack();
  }

  return { unsubscribeClicked, unsubscribeSelected };
}
