'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Phone, Shield, Heart, Clock } from 'lucide-react';
import { useI18n } from '@/utils/i18n';
import { useConversationStore } from '@/stores/conversationStore';
import { useLanguageStore } from '@/stores/languageStore';

interface SafetyAlert {
  id: string;
  type: 'crisis' | 'warning' | 'info';
  message: string;
  timestamp: Date;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export function SafetyProtocols() {

  const { messages } = useConversationStore();
  const [alerts, setAlerts] = useState<SafetyAlert[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [lastCheck, setLastCheck] = useState(new Date());
  const { t } = useI18n();
  const { getLocale } = useLanguageStore();
  const lang = getLocale();
  // Simulate safety monitoring (in real app, this would come from the backend)
  useEffect(() => {
    if (!isMonitoring) return;

    setLastCheck(new Date());

    const newAlerts = messages
      .filter(msg => msg.type === 'assistant')
      .map(msg => ({
        id: msg.id,
        type: 'crisis' as const,
        message: t('alerts.crisisDetected'),
        timestamp: new Date(msg.timestamp),
        severity: 'critical' as const
      }));

    // Always create a copy before reverse() since reverse() mutates
    setAlerts([...newAlerts].slice(-5).reverse());
  }, [messages, isMonitoring]);

  const getSeverityColor = (severity: SafetyAlert['severity']) => {
    const colors = {
      low: 'text-green-600 bg-green-100 border-green-200',
      medium: 'text-yellow-600 bg-yellow-100 border-yellow-200',
      high: 'text-orange-600 bg-orange-100 border-orange-200',
      critical: 'text-red-600 bg-red-100 border-red-200'
    };
    return colors[severity];
  };

  const getTypeIcon = (type: SafetyAlert['type']) => {
    switch (type) {
      case 'crisis':
        return <AlertTriangle size={16} className="text-red-600" />;
      case 'warning':
        return <Shield size={16} className="text-yellow-600" />;
      case 'info':
        return <Heart size={16} className="text-blue-600" />;
    }
  };

  const formatTime = (date: Date) => {
    const locale = lang === 'ar' ? 'ar-SA' : 'en-US';
    return new Intl.DateTimeFormat(locale, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  };

  const emergencyContacts = [
    {
      nameKey: 'safety.contacts.name.psychHotline',
      number: '8000-4444',
      availabilityKey: 'safety.contacts.availability.24_7'
    },
    {
      nameKey: 'safety.contacts.name.crisisCenter',
      number: '8000-1111',
      availabilityKey: 'safety.contacts.availability.24_7'
    },
    {
      nameKey: 'safety.contacts.name.supportLine',
      number: '8000-2222',
      availabilityKey: 'safety.contacts.availability.8_24'
    }
  ] as const;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-900 arabic-text mb-4">
        {t('safety.title')}
      </h3>

      {/* Monitoring Status */}
      <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 space-x-reverse">
            <div className={`w-3 h-3 rounded-full ${
              isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
            }`}></div>
            <div>
              <p className="text-sm font-medium text-green-800 arabic-text">
                {isMonitoring ? t('safety.monitoring.active') : t('safety.monitoring.stopped')}
              </p>
              <p className="text-xs text-green-600 arabic-text">
                {t('safety.lastCheck')} {formatTime(lastCheck)}
              </p>
            </div>
          </div>
          
          <button
            onClick={() => setIsMonitoring(!isMonitoring)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              isMonitoring 
                ? 'bg-red-100 text-red-800 hover:bg-red-200' 
                : 'bg-green-100 text-green-800 hover:bg-green-200'
            }`}
          >
            {isMonitoring ? t('safety.toggle.stop') : t('safety.toggle.start')}
          </button>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 arabic-text mb-3">
          {t('safety.recentAlerts')}
        </h4>
        
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {alerts.length === 0 ? (
            <div className="text-center py-4">
              <Heart size={24} className="text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500 arabic-text">
                {t('safety.noAlerts.ar')}
              </p>
              <p className="text-xs text-gray-400 english-text">
                {t('safety.noAlerts.en')}
              </p>
            </div>
          ) : (
            alerts.map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`p-3 rounded-lg border ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start space-x-2 space-x-reverse">
                  {getTypeIcon(alert.type)}
                  <div className="flex-1">
                    <p className="text-xs font-medium arabic-text">
                      {alert.message}
                    </p>
                    <p className="text-xs opacity-75 arabic-text mt-1">
                      {formatTime(alert.timestamp)}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Emergency Contacts */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 arabic-text mb-3">
          {t('safety.contacts.title')}
        </h4>
        
        <div className="space-y-2">
          {emergencyContacts.map((contact, index) => (
            <div
              key={index}
              className="p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900 arabic-text">
                    {t(contact.nameKey)}
                  </p>
                  <p className="text-xs text-gray-600 arabic-text">
                    {t('safety.contacts.available')} {t(contact.availabilityKey)}
                  </p>
                </div>
                
                <a
                  href={`tel:${contact.number}`}
                  className="flex items-center space-x-1 space-x-reverse px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <Phone size={14} />
                  <span className="text-sm font-medium">
                    {contact.number}
                  </span>
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Safety Statistics */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-blue-50 rounded-lg text-center">
          <p className="text-lg font-bold text-blue-600">
            {alerts.filter(a => a.severity === 'critical').length}
          </p>
          <p className="text-xs text-blue-800 arabic-text">
            {t('safety.stats.emergencies')}
          </p>
        </div>
        
        <div className="p-3 bg-green-50 rounded-lg text-center">
          <p className="text-lg font-bold text-green-600">
            {Math.floor(Date.now() / 1000) % 100}
          </p>
          <p className="text-xs text-green-800 arabic-text">
            {t('safety.stats.safeMinutes')}
          </p>
        </div>
      </div>

      {/* Crisis Intervention Info */}
      <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
        <div className="flex items-center space-x-2 space-x-reverse">
          <AlertTriangle size={16} className="text-red-600" />
          <p className="text-sm text-red-800 arabic-text font-medium">
            {t('safety.crisis.title')}
          </p>
        </div>
        <p className="text-xs text-red-700 arabic-text mt-1">
          {t('safety.crisis.instruction')}
        </p>
      </div>
    </div>
  );
}
