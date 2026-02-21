/** @type {import('next').NextConfig} */
// On Vercel/production, default to Railway backend when NEXT_PUBLIC_API_URL is not set
const isVercel = process.env.VERCEL === '1'
const defaultApiUrl = isVercel
  ? 'https://borge-accounting-production.up.railway.app/api/v1'
  : 'http://localhost:8000/api/v1'

const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || defaultApiUrl,
  },
}

module.exports = nextConfig
