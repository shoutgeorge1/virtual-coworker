import { readFileSync } from "node:fs";
import { createStore } from "../lib/db/store";

for (const line of readFileSync(".env.local", "utf8").split("\n")) {
  const t = line.trim();
  if (!t || t.startsWith("#") || !t.includes("=")) continue;
  const i = t.indexOf("=");
  const k = t.slice(0, i);
  let v = t.slice(i + 1);
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    v = v.slice(1, -1);
  }
  if (!(k in process.env)) process.env[k] = v;
}

async function main() {
  const store = createStore();
  await store.ensureSchema();
  const counts = await store.countRows();
  console.log(JSON.stringify({ schema: "ok", counts }, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
