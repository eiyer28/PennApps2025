/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    outputFileTracingIncludes: {},
  },
  outputFileTracing: false,
};

export default nextConfig;
