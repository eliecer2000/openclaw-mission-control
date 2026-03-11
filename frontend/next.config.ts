import type { NextConfig } from "next";

const rawOrigins = process.env.NEXT_PUBLIC_ALLOWED_DEV_ORIGINS ?? "";
const allowedDevOrigins = rawOrigins
  ? rawOrigins
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
  : ["localhost", "127.0.0.1"];

const nextConfig: NextConfig = {
  allowedDevOrigins,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "img.clerk.com",
      },
    ],
  },
};

export default nextConfig;
