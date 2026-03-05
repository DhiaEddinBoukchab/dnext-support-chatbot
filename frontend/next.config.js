/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  compiler: {
    reactCompiler: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
}

module.exports = nextConfig
