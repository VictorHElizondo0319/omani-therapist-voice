import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type SupportedLanguage = 'english' | 'omani-arabic';

export interface LanguageState {
  language: SupportedLanguage;
  setLanguage: (language: SupportedLanguage) => void;
  getDirection: () => 'ltr' | 'rtl';
  getLocale: () => 'en' | 'ar';
  translateEnabled: boolean;
  setTranslateEnabled: (enabled: boolean) => void;
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set, get) => ({
      language: 'english',
      translateEnabled: false,
      setLanguage: (language) => set({ language }),
      setTranslateEnabled: (enabled) => set({ translateEnabled: enabled }),
      getDirection: () => (get().language === 'omani-arabic' ? 'rtl' : 'ltr'),
      getLocale: () => (get().language === 'omani-arabic' ? 'ar' : 'en'),
    }),
    {
      name: 'language-preference',
      partialize: (state) => ({ language: state.language, translateEnabled: state.translateEnabled }),
    }
  )
);


