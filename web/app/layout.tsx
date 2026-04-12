import type { Metadata } from 'next';
import { Inter, Space_Grotesk } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-body', display: 'swap' });
const space = Space_Grotesk({ subsets: ['latin'], variable: '--font-headline', display: 'swap' });

export const metadata: Metadata = {
  title: 'KHOps Architect',
  description: 'Enterprise MLOps dashboard for architecture health, model registry, and deployment observability.',
  metadataBase: new URL('http://localhost')
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${space.variable} bg-background text-on-surface font-body`}>
        {children}
      </body>
    </html>
  );
}
