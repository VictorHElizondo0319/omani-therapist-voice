'use client';

import { PropsWithChildren, useEffect } from 'react';
import { useLanguageStore } from '@/stores/languageStore';

interface LanguageHtmlProps {
  className?: string;
}

export default function LanguageHtml({ children, className }: PropsWithChildren<LanguageHtmlProps>) {
  const { getDirection, getLocale } = useLanguageStore();
  const dir = getDirection();
  const lang = getLocale();

  // Ensure html attributes update on change
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('dir', dir);
      document.documentElement.setAttribute('lang', lang);
    }
  }, [dir, lang]);

  // Next.js requires returning <html> from root layout; we proxy it here
  return (
    <html lang={lang} dir={dir} className={className}>
      {children}
    </html>
  );
}


