import { createApp } from "./app";
import { createRedis } from "./cache";
import { config } from "./config";

const app = createApp(createRedis());

app.listen(config.backendPort);

console.log(`backend listening on ${config.backendPort}`);
