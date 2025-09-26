'use client';

import { useState, useEffect } from 'react';
import { VoiceInterface } from '@/components/VoiceInterface';
import { ConversationHistory } from '@/components/ConversationHistory';
import { SafetyProtocols } from '@/components/SafetyProtocols';
import { Header } from '@/components/Header';
import { useConversationStore } from '@/stores/conversationStore';
import { useSpeechStore } from '@/stores/speechStore';
import { useI18n } from '@/utils/i18n';

export default function HomePage() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [showSafetyInfo, setShowSafetyInfo] = useState(true);
  const { t } = useI18n();
  
  const { sessionId, isConnected, initializeSession} = useConversationStore();
  const { initializeSpeech } = useSpeechStore();

  useEffect(() => {
    const initialize = async () => {
      try {
        await initializeSession();
        await initializeSpeech();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize application:', error);
      }
    };

    initialize();
  }, [initializeSession, initializeSpeech]);

  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600 arabic-text">{t('loading.app')}</p>
          <p className="text-gray-500 text-sm mt-2 english-text">{t('loading.app')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Safety Information Banner */}
        {showSafetyInfo && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-amber-800 arabic-text mb-2">
                  {t('safety.info.title')}
                </h3>
                <p className="text-amber-700 arabic-text mb-2">{t('safety.info.body2')}</p>
                <p className="text-amber-600 text-sm english-text">{t('safety.info.body1')}</p>
              </div>
              <button
                onClick={() => setShowSafetyInfo(false)}
                className="ml-4 text-amber-600 hover:text-amber-800"
                aria-label={t('safety.close')}
              >
                ✕
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Voice Interface */}
          <div className="lg:col-span-2 space-y-6">
            <VoiceInterface />
            <ConversationHistory />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <SafetyProtocols />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center">
            <p className="text-gray-600 arabic-text mb-2">
              © 2024 OMANI-Therapist-Voice. {t('footer.rights')}
            </p>
            <p className="text-gray-500 text-sm english-text">
              {t('footer.tagline')}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
