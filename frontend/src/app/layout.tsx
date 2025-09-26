import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI受付システム',
  description: 'OpenAI Realtime APIを使用したリアルタイム音声受付システム',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          <header className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              AI受付システム
            </h1>
            <p className="text-gray-600">
              音声でお気軽にお話しください
            </p>
          </header>
          <main>
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
