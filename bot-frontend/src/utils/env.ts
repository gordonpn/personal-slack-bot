import { config } from "dotenv";
import { resolve } from "path";

if (process.env.NODE_ENV !== "production") {
  console.log("Loading environment variables from file");
  const pathToConfig = "../../.env";
  config({ path: resolve(__dirname, pathToConfig) });
}
