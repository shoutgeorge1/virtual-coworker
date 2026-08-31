import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  // Static HTML lives in public/ (copied at build). No App Router UI pages.
  poweredByHeader: false,
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
