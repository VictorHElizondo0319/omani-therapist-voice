'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, Volume2, VolumeX, AlertTriangle, Heart } from 'lucide-react';
import { Message } from '@/stores/conversationStore';
import { useLanguageStore } from '@/stores/languageStore';
import { useI18n } from '@/utils/i18n';
import { useEffect } from 'react';
import { translateText } from '@/utils/translate';

interface ConversationBubbleProps {
  message: Message;
}

export function ConversationBubble({ message }: ConversationBubbleProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const { language, translateEnabled } = useLanguageStore();
  const { t } = useI18n();
  const [translatedContent, setTranslatedContent] = useState<string | null>(null);
  const [showOriginal, setShowOriginal] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      if (!translateEnabled) {
        setTranslatedContent(null);
        return;
      }
      const to = language === 'omani-arabic' ? 'ar' : 'en';
      const from: 'en' | 'ar' | undefined = undefined; // unknown; backend can auto-detect
      const translated = await translateText(message.content, from, to);
      if (!cancelled) setTranslatedContent(translated);
    }
    run();
    return () => { cancelled = true; };
  }, [message.content, language, translateEnabled]);

  const handlePlayAudio = async () => {
    if (!message.audio) return;
    
    try {
      setIsPlaying(true);
      // Strip prefix if present (data:audio/wav;base64,...)
      let base64Data = message.audio;
      if (base64Data.startsWith("data:")) {
        base64Data = base64Data.split(",")[1];
      }
      console.log(base64Data)
      // Convert Base64 to binary
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Create Blob + Object URL
      const blob = new Blob([bytes], { type: "audio/wav" });
      const audioUrl = URL.createObjectURL(blob);

      // Play the audio from blob URL
      const audio = new Audio(audioUrl);
      await audio.play();

      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };

    } catch (error) {
      console.error("Error playing audio:", error);
      setIsPlaying(false);
    }

  };

  const formatTimestamp = (ts: Date | string | undefined) => {
    if (!ts) return '';
    const date = ts instanceof Date ? ts : new Date(ts);
    if (isNaN(date.getTime())) return '';
    const locale = language === 'omani-arabic' ? 'ar-SA' : 'en-US';
    return new Intl.DateTimeFormat(locale, {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(date);
  };

  const getEmotionColor = (emotion: string) => {
    const colors = {
      'anxiety': 'text-yellow-600 bg-yellow-100',
      'depression': 'text-blue-600 bg-blue-100',
      'anger': 'text-red-600 bg-red-100',
      'fear': 'text-purple-600 bg-purple-100',
      'sadness': 'text-indigo-600 bg-indigo-100',
      'neutral': 'text-gray-600 bg-gray-100',
      'happy': 'text-green-600 bg-green-100'
    };
    return colors[emotion as keyof typeof colors] || colors.neutral;
  };

  const getCrisisLevelColor = (level: string) => {
    const colors = {
      'low': 'text-green-600 bg-green-100',
      'medium': 'text-yellow-600 bg-yellow-100',
      'high': 'text-orange-600 bg-orange-100',
      'critical': 'text-red-600 bg-red-100'
    };
    return colors[level as keyof typeof colors] || colors.low;
  };

  return (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`conversation-bubble ${
          message.type === 'user' ? 'user' : 'assistant'
        } ${message.isError ? 'crisis' : ''}`}
      >
        {/* Message content */}
        <div className="space-y-2">
          <div className={`${message.type === 'user' ? 'text-white' : 'text-gray-800'} arabic-text`}>
            {translateEnabled && translatedContent && !showOriginal ? (
              <>
                <p>{translatedContent}</p>
                <button
                  className="mt-1 text-xs underline opacity-80"
                  onClick={() => setShowOriginal(true)}
                >
                  {t('translate.showOriginal')}
                </button>
              </>
            ) : (
              <>
                <p>{message.content}</p>
                {translateEnabled && translatedContent && (
                  <button
                    className="mt-1 text-xs underline opacity-80"
                    onClick={() => setShowOriginal(false)}
                  >
                    {t('translate.showTranslated')}
                  </button>
                )}
              </>
            )}
          </div>
          
          {/* Audio controls */}
          {message.audio && (
            <div className="flex items-center space-x-2 space-x-reverse">
              <button
                onClick={handlePlayAudio}
                disabled={isPlaying}
                className={`p-2 rounded-full transition-colors ${
                  message.type === 'user' 
                    ? 'bg-white bg-opacity-20 hover:bg-opacity-30 text-white' 
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                }`}
              >
                {isPlaying ? (
                  <Pause size={16} />
                ) : (
                  <Play size={16} />
                )}
              </button>
              
              <span className={`text-xs ${
                message.type === 'user' ? 'text-white text-opacity-80' : 'text-gray-500'
              }`}>
                {isPlaying ? t('audio.playing') : t('audio.pressToListen')}
              </span>
            </div>
          )}
          
          {/* Timestamp */}
          <div className={`text-xs ${
            message.type === 'user' ? 'text-white text-opacity-70' : 'text-gray-500'
          }`}>
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
        
        {/* Analysis information */}
        {message.analysis && message.type === 'assistant' && (
          <div className="mt-3 pt-3 border-t border-gray-200 border-opacity-50">
            <button
              onClick={() => setShowAnalysis(!showAnalysis)}
              className="text-xs text-gray-500 hover:text-gray-700 transition-colors arabic-text"
            >
              {showAnalysis ? t('analysis.hide') : t('analysis.show')}
            </button>
            
            {showAnalysis && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-2 space-y-2"
              >
                {/* Emotional state */}
                {message.analysis.emotional_state && (
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <Heart size={14} className="text-gray-400" />
                    <span className="text-xs text-gray-600 arabic-text">{t('analysis.emotionalState')}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getEmotionColor(message.analysis.emotional_state)}`}>
                      {message.analysis.emotional_state}
                    </span>
                  </div>
                )}
                
                {/* Crisis assessment */}
                {message.analysis.crisis_assessment && (
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <AlertTriangle size={14} className="text-gray-400" />
                    <span className="text-xs text-gray-600 arabic-text">{t('analysis.riskLevel')}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getCrisisLevelColor(message.analysis.crisis_assessment.risk_level)}`}>
                      {message.analysis.crisis_assessment.risk_level}
                    </span>
                  </div>
                )}
                
                {/* Cultural adaptations */}
                {message.culturalAdaptations && message.culturalAdaptations.length > 0 && (
                  <div className="mt-2">
                    <span className="text-xs text-gray-600 arabic-text">{t('analysis.culturalAdaptations')}</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {message.culturalAdaptations.map((adaptation, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                        >
                          {adaptation}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        )}
        
        {/* Crisis warning */}
        {message.analysis?.crisis_assessment?.risk_level === 'critical' && (
          <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2 space-x-reverse">
              <AlertTriangle size={16} className="text-red-600" />
              <span className="text-xs text-red-800 arabic-text font-medium">
                {t('crisis.warning')}
              </span>
            </div>
            <p className="text-xs text-red-700 arabic-text mt-1">
              {t('crisis.hotline')}
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
