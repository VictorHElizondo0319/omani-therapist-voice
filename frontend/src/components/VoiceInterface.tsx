'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Pause, Play } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSpeechStore } from '@/stores/speechStore';
import { useConversationStore } from '@/stores/conversationStore';
import { AudioVisualizer } from './AudioVisualizer';
import { ConversationBubble } from './ConversationBubble';
import { useI18n } from '@/utils/i18n';

export function VoiceInterface() {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const { 
    startRecording, 
    stopRecording, 
    playAudio, 
    stopAudio,
    isSupported 
  } = useSpeechStore();
  const { t } = useI18n();
  
  const { 
    addMessage, 
    messages, 
    sessionId,
    isConnected,
    addConversation,
    endConversation, 
  } = useConversationStore();

  useEffect(() => {
    // Check for microphone permissions
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(() => {
        console.log('Microphone access granted');
      })
      .catch((error) => {
        console.error('Microphone access denied:', error);
      });
  }, []);

  const handleStartRecording = async () => {
    if (!isSupported) {
      alert(t('error.noSpeechSupport'));
      return;
    }

    try {
      setIsRecording(true);
      setCurrentTranscript('');
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      });
      
      streamRef.current = stream;
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks: BlobPart[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        
        // Convert to base64 for transmission
        const reader = new FileReader();
        reader.onload = async () => {
          const base64Audio = reader.result as string;
          await processAudioMessage(base64Audio);
        };
        reader.readAsDataURL(audioBlob);
      };
      
      // Start recording
      mediaRecorder.start(1000); // Collect data every second
      
      // Monitor audio levels
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      microphone.connect(analyser);
      
      analyser.fftSize = 256;
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      
      const updateAudioLevel = () => {
        if (isRecording) {
          analyser.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
          setAudioLevel(average);
          requestAnimationFrame(updateAudioLevel);
        }
      };
      
      updateAudioLevel();
      
    } catch (error) {
      console.error('Error starting recording:', error);
      setIsRecording(false);
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      
      // Stop all tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      
      setIsRecording(false);
      setAudioLevel(0);
    }
  };

  const processAudioMessage = async (audioData: string) => {
    setIsProcessing(true);
    
    try {
      // Add user message to conversation
      
      const userMessage = {
        id: Date.now().toString(),
        type: 'user' as const,
        content: currentTranscript || t('voice.audioMessage'),
        audio: audioData,
        timestamp: new Date(),
        isAudio: true
      };
      
      addMessage(userMessage);
      const requestBody = {
        transcript: currentTranscript || "", // always send text, even empty string
        audio_metadata: {
          mime_type: "audio/webm",
          base64: audioData.split(",")[1] // strip header, keep only Base64
        },
        session_context: {
          sessionId
        }
      };
      // Send to backend for processing
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/${sessionId}/process_voice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        throw new Error('Failed to process audio');
      }
      
      const result = await response.json();
      console.log('Backend response:', result);
      // Add assistant response
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant' as const,
        content: result.response.text,
        audio: result.audio,
        timestamp: new Date(),
        isAudio: true,
        analysis: result.analysis,
        culturalAdaptations: result.cultural_adaptations || true
      };
      
      addMessage(assistantMessage);
      
      // Play assistant response if audio is available
      if (result.audio) {
        await playAudioResponse(result.audio);
      }
      
    } catch (error) {
      console.error('Error processing audio:', error);
      
      // Add error message
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant' as const,
        content: t('error.audioProcessing'),
        timestamp: new Date(),
        isError: true
      };
      
      addMessage(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudioResponse = async (audioData: string) => {
    try {
      setIsPlaying(true);
      
      // Convert base64 to blob and create audio URL
      const binaryString = atob(audioData);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(blob);
      
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        await audioRef.current.play();
        
        audioRef.current.onended = () => {
          setIsPlaying(false);
          URL.revokeObjectURL(audioUrl);
        };
      }
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
    }
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-2xl font-bold text-gray-900 arabic-text mb-6">
        {t('voice.title')}
      </h2>
      {/* Quick Actions */}
      <div className="flex justify-between gap-2 items-center bg-white rounded-lg shadow-sm p-6">
        {/* Connection Status */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="flex items-center space-x-2 space-x-reverse">
            <div className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-600 arabic-text">
              {isConnected ? t('connection.connected') : t('connection.disconnected')}
            </span>
            <span className="text-xs text-gray-500 english-text">
              Session ID: {sessionId?.slice(0, 8)}...
            </span>
          </div>
        </div>
        <div className='text-sm'>
          <button
            onClick={() => addConversation()} 
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors arabic-text">
            {t('actions.newConversation')}
          </button>
          <button 
            onClick={() => endConversation()}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors arabic-text">
            {t('actions.endSession')}
          </button>
        </div>
      </div>
      {/* Audio Element */}
      <audio ref={audioRef} className="hidden" />
      
      {/* Voice Recording Interface */}
      <div className="flex flex-col items-center space-y-6">
        {/* Main Voice Button */}
        <div className="relative">
          <motion.button
            onClick={isRecording ? handleStopRecording : handleStartRecording}
            disabled={isProcessing || !isConnected}
            className={`voice-button ${isRecording ? 'recording' : ''} ${
              isProcessing ? 'processing' : ''
            } ${!isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{ width: '120px', height: '120px' }}
          >
            <AnimatePresence mode="wait">
              {isRecording ? (
                <motion.div
                  key="stop"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  className="flex items-center justify-center"
                >
                  <MicOff size={48} />
                </motion.div>
              ) : isProcessing ? (
                <motion.div
                  key="processing"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  className="flex items-center justify-center"
                >
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
                </motion.div>
              ) : (
                <motion.div
                  key="mic"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  className="flex items-center justify-center"
                >
                  <Mic size={48} />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
          
          {/* Audio Level Indicator */}
          {isRecording && (
            <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2">
              <AudioVisualizer level={audioLevel} />
            </div>
          )}
        </div>
        
        {/* Status Text */}
        <div className="text-center">
          <p className="text-lg font-medium text-gray-700 arabic-text">
            {isRecording && t('voice.status.recording')}
            {isProcessing && t('voice.status.processing')}
            {!isRecording && !isProcessing && isConnected && t('voice.status.clickToSpeak')}
            {!isConnected && t('voice.status.notConnected')}
          </p>
          <p className="text-sm text-gray-500 english-text mt-1">
            {isRecording && t('voice.status.recording')}
            {isProcessing && t('voice.status.processing')}
            {!isRecording && !isProcessing && isConnected && t('voice.status.clickToSpeak')}
            {!isConnected && t('voice.status.notConnected')}
          </p>
        </div>
        
        {/* Playback Controls */}
        {messages.some(msg => msg.audio) && (
          <div className="flex items-center space-x-4 space-x-reverse">
            <button
              onClick={handlePlayPause}
              className="p-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              disabled={isProcessing}
            >
              {isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>
            
            <div className="flex items-center space-x-2 space-x-reverse">
              <Volume2 size={20} className="text-gray-500" />
              <span className="text-sm text-gray-600 arabic-text">
                {t('voice.listenLast')}
              </span>
            </div>
          </div>
        )}
      </div>
      
      {/* Current Transcript Display */}
      {currentTranscript && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-gray-50 rounded-lg"
        >
          <p className="text-sm text-gray-600 arabic-text mb-2">{t('voice.currentTranscript')}</p>
          <p className="text-gray-800 arabic-text">{currentTranscript}</p>
        </motion.div>
      )}
      
      {/* Quick Actions */}
      <div className="mt-6 flex justify-center space-x-4 space-x-reverse">
        <button
          onClick={() => setCurrentTranscript('')}
          className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors arabic-text"
          disabled={isRecording || isProcessing}
        >
          {t('voice.clearText')}
        </button>
        
        <button
          onClick={handleStopRecording}
          className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors arabic-text"
          disabled={!isRecording}
        >
          {t('voice.stopRecording')}
        </button>
      </div>
    </div>
  );
}
