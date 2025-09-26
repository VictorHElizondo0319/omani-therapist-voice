import type { Metadata } from 'next';
import { Inter, Noto_Sans_Arabic } from 'next/font/google';
import './globals.css';
import dynamic from 'next/dynamic';
const LanguageAttributes = dynamic(() => import('@/components/LanguageAttributes'), { ssr: false });

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const notoSansArabic = Noto_Sans_Arabic({ 
  subsets: ['arabic'],
  variable: '--font-arabic',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'OMANI-Therapist-Voice | مساعد الصحة النفسية',
  description: 'A culturally sensitive mental health support chatbot for Omani Arabic speakers',
  keywords: ['mental health', 'therapy', 'Omani Arabic', 'chatbot', 'الصحة النفسية'],
  authors: [{ name: 'OMANI-Therapist-Voice Team' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" dir="ltr" className={`${inter.variable} ${notoSansArabic.variable}`}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={`${inter.className} ${notoSansArabic.className} antialiased`}>
        <LanguageAttributes />
        <div id="root">
          {children}
        </div>
      </body>
    </html>
  );
}
