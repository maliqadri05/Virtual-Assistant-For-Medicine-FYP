/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  eslint: {
    dirs: ['app', 'components', 'services', 'utils', 'hooks'],
  },
  redirects: async () => [
    {
      source: '/chat',
      destination: '/chat/new',
      permanent: false,
    },
  ],
};

module.exports = nextConfig;
