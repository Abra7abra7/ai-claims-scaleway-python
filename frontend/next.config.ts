import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  // Enable React strict mode
  reactStrictMode: true,
  
  // Output standalone for Docker
  output: "standalone",
};

export default withNextIntl(nextConfig);
