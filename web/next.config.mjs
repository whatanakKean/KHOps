/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: process.env.NEXT_PUBLIC_API_BASE ? `${process.env.NEXT_PUBLIC_API_BASE}/:path*` : 'http://127.0.0.1:8000/api/v1/:path*',
      },
    ];
  },
};

export default nextConfig;
