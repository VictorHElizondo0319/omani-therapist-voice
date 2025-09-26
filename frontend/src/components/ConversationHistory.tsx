'use client';

import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useConversationStore } from '@/stores/conversationStore';
import { ConversationBubble } from './ConversationBubble';
import { AudioVisualizer } from './AudioVisualizer';
import { useI18n } from '@/utils/i18n';

export function ConversationHistory() {
  const { messages, isProcessing } = useConversationStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { t } = useI18n();
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-2xl font-bold text-gray-900 arabic-text mb-6">
        {t('history.title')}
      </h2>
      
      <div className="h-96 overflow-y-auto space-y-4 pr-2">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <ConversationBubble message={message} />
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* Processing indicator */}
        {isProcessing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center space-x-2 space-x-reverse justify-start"
          >
            <div className="conversation-bubble assistant">
              <div className="flex items-center space-x-2 space-x-reverse">
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
                <span className="text-sm text-gray-600 arabic-text">
                  {t('history.thinking')}
                </span>
              </div>
            </div>
          </motion.div>
        )}
        
        {/* Empty state */}
        {messages.length === 0 && !isProcessing && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 arabic-text mb-2">
              {t('history.empty.start')}
            </h3>
            <p className="text-gray-500 arabic-text">
              {t('history.empty.hint.ar')}
            </p>
            <p className="text-gray-400 text-sm english-text mt-2">
              {t('history.empty.hint.en')}
            </p>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Conversation stats */}
      {messages.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span className="arabic-text">
              {t('history.stats.messages.ar')} {messages.length}
            </span>
            <span className="english-text">
              {t('history.stats.messages.en')} {messages.length}
            </span>
          </div>
          
          {/* Cultural adaptations used */}
          {messages.some(msg => msg.culturalAdaptations && msg.culturalAdaptations.length > 0) && (
            <div className="mt-2">
              <div className="flex flex-wrap gap-2">
                {Array.from(new Set(
                  messages
                    .filter(msg => msg.culturalAdaptations)
                    .flatMap(msg => msg.culturalAdaptations || [])
                )).map(adaptation => (
                  <span
                    key={adaptation}
                    className="cultural-indicator"
                  >
                    {adaptation}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
