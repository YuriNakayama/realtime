/** @type {import('next').NextConfig} */
const nextConfig = {
  // experimental: {
  //   // React 19の実験的機能を有効化 - 一時的に無効化
  //   reactCompiler: true,
  // },
  // WebSocketサポートのためのcustom server設定
  async rewrites() {
    return [
      {
        source: '/ws/:path*',
        destination: 'http://localhost:8000/ws/:path*',
      },
    ];
  },
  // CORS設定
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: 'http://localhost:8000',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET,POST,OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
