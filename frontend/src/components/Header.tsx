'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Settings, Info, Globe, Headphones } from 'lucide-react';
import { useLanguageStore } from '@/stores/languageStore';
import { useI18n } from '@/utils/i18n';

export function Header() {
  const [showSettings, setShowSettings] = useState(false);
  const { language, setLanguage, translateEnabled, setTranslateEnabled } = useLanguageStore();
  const { t } = useI18n();

  // Close settings on language change for better UX
  useEffect(() => {
    if (showSettings) {
      setShowSettings(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language]);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4 space-x-reverse">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
              <Headphones className="w-6 h-6 text-white" />
            </div>
            
            <div>
              <h1 className="text-2xl font-bold text-gray-900 arabic-text">
                {t('app.title')}
              </h1>
              <p className="text-sm text-gray-600 english-text">
                {t('app.brand')}
              </p>
            </div>
          </div>

          {/* Navigation and Controls */}
          <div className="flex items-center space-x-4 space-x-reverse">
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="flex items-center space-x-2 space-x-reverse px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <Globe size={16} className="text-gray-600" />
                <span className="text-sm text-gray-700 arabic-text">
                  {language === 'omani-arabic' ? t('language.arabic') : t('language.english')}
                </span>
              </button>

              {/* Settings Dropdown */}
              {showSettings && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-full right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
                >
                  <div className="p-4">
                    <h3 className="text-sm font-medium text-gray-900 arabic-text mb-3">
                      {t('settings.title')}
                    </h3>
                    
                    {/* Language Selection */}
                    <div className="mb-4">
                      <label className="block text-xs font-medium text-gray-700 arabic-text mb-2">
                        {t('settings.language')}
                      </label>
                      <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value as any)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="omani-arabic">{t('language.arabic')}</option>
                        <option value="english">{t('language.english')}</option>
                      </select>
                    </div>

                    {/* Translate Messages Toggle */}
                    <div className="mb-4">
                      <label className="flex items-center space-x-2 space-x-reverse">
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          checked={translateEnabled}
                          onChange={(e) => setTranslateEnabled(e.target.checked)}
                        />
                        <span className="text-xs text-gray-700 arabic-text">
                          {t('translate.toggle')}
                        </span>
                      </label>
                    </div>

                    {/* Voice Settings */}
                    <div className="mb-4">
                      <label className="block text-xs font-medium text-gray-700 arabic-text mb-2">
                        {t('settings.voice')}
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="male">{t('settings.voice.male')}</option>
                        <option value="female">{t('settings.voice.female')}</option>
                      </select>
                    </div>

                    {/* Cultural Sensitivity Level */}
                    <div className="mb-4">
                      <label className="block text-xs font-medium text-gray-700 arabic-text mb-2">
                        {t('settings.culturalSensitivity')}
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="high">{t('settings.culturalSensitivity.high')}</option>
                        <option value="medium">{t('settings.culturalSensitivity.medium')}</option>
                        <option value="low">{t('settings.culturalSensitivity.low')}</option>
                      </select>
                    </div>

                    {/* Privacy Settings */}
                    <div className="mb-4">
                      <label className="flex items-center space-x-2 space-x-reverse">
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          defaultChecked
                        />
                        <span className="text-xs text-gray-700 arabic-text">
                          {t('settings.privacy.localOnly')}
                        </span>
                      </label>
                    </div>

                    <button
                      onClick={() => setShowSettings(false)}
                      className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm arabic-text"
                    >
                      {t('settings.save')}
                    </button>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Info Button */}
            <button className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
              <Info size={16} className="text-gray-600" />
            </button>

            {/* Connection Status */}
            <div className="flex items-center space-x-2 space-x-reverse">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600 arabic-text">
                متصل
              </span>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-4 space-x-reverse">
              <span className="arabic-text">
                جلسة آمنة ومشفرة
              </span>
              <span className="english-text">
                Secure & Encrypted Session
              </span>
            </div>
            
            <div className="flex items-center space-x-4 space-x-reverse">
              <span className="arabic-text">
                متوافق مع معايير HIPAA
              </span>
              <span className="english-text">
                HIPAA Compliant
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
