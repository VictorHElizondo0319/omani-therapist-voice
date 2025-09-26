import { useLanguageStore } from '@/stores/languageStore';

// Simple placeholder translator: returns original if languages match.
// Optionally calls backend endpoint if provided.
export async function translateText(
  text: string,
  fromLang: 'en' | 'ar' | undefined,
  toLang: 'en' | 'ar'
): Promise<string> {
  if (!text) return text;
  if (fromLang && fromLang === toLang) return text;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  try {
    if (apiUrl) {
      const res = await fetch(`${apiUrl}/api/v1/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, to: toLang, from: fromLang }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data?.translated) return data.translated as string;
      }
    }
  } catch (e) {
    // Fallback to original on any error
    console.warn('Translation failed, falling back to original.', e);
  }
  return text;
}


