import {
  AckFn,
  BlockElementAction,
  ButtonClick,
  DialogSubmitAction,
  DialogValidation,
  InteractiveAction,
  Logger,
  SayArguments,
  WorkflowStepEdit,
} from "@slack/bolt";
import { Action } from "./actions";

export const subscribe = async ({
  payload,
  ack,
  logger,
}: {
  payload:
    | DialogSubmitAction
    | WorkflowStepEdit
    | BlockElementAction
    | InteractiveAction;
  ack: AckFn<void> | AckFn<string | SayArguments> | AckFn<DialogValidation>;
  logger: Logger;
}) => {
  await ack();
  logger.debug(`${Action.Subscribe} clicked`);
  logger.debug(`Will subscribe to: ${(payload as ButtonClick).value}`);
};
