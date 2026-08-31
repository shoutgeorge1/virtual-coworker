#!/usr/bin/env node
/**
 * Copy the existing static dashboard into public/ for Next.js deploy.
 * Bake scripts keep writing to xray/ root — this is build-time only.
 * Does not touch runtime sync storage.
 */
import { cpSync, existsSync, mkdirSync, rmSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const root = new URL("..", import.meta.url).pathname;
const pub = join(root, "public");

mkdirSync(pub, { recursive: true });

const skip = new Set([
  "node_modules",
  ".next",
  ".vercel",
  ".git",
  "app",
  "lib",
  "scripts",
  "__tests__",
  "public",
  "package.json",
  "package-lock.json",
  "tsconfig.json",
  "next.config.ts",
  "next.config.js",
  "next.config.mjs",
  "next-env.d.ts",
  "vitest.config.ts",
  "vercel.json",
  ".gitignore",
  ".env",
  ".env.local",
  ".env.example",
  "README.md",
  "serve.sh",
  "smoke-live.mjs",
]);

for (const name of readdirSync(root)) {
  if (skip.has(name)) continue;
  if (name.startsWith("tmp-")) continue;
  if (name.startsWith(".")) continue;
  const src = join(root, name);
  const dest = join(pub, name);
  const st = statSync(src);
  if (st.isDirectory()) {
    rmSync(dest, { recursive: true, force: true });
    cpSync(src, dest, { recursive: true });
  } else {
    cpSync(src, dest);
  }
}

if (!existsSync(join(pub, "launch-control.html"))) {
  console.error("sync-static-to-public: launch-control.html missing after copy");
  process.exit(1);
}

console.log("Synced static dashboard → public/");
