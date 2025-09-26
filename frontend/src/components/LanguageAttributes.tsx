'use client';

import { useEffect } from 'react';
import { useLanguageStore } from '@/stores/languageStore';

export default function LanguageAttributes() {
  const { getDirection, getLocale } = useLanguageStore();
  const dir = getDirection();
  const lang = getLocale();

  useEffect(() => {
    document.documentElement.setAttribute('dir', dir);
    document.documentElement.setAttribute('lang', lang);
  }, [dir, lang]);

  return null;
}


