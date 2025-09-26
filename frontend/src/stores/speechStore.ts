import { create } from 'zustand';

export interface SpeechState {
  // State
  isSupported: boolean;
  isRecording: boolean;
  isPlaying: boolean;
  audioLevel: number;
  currentTranscript: string;
  
  // Actions
  initializeSpeech: () => Promise<boolean>;
  startRecording: () => Promise<MediaStream>;
  stopRecording: () => void;
  playAudio: (audioData: string) => Promise<void>;
  stopAudio: () => void;
  setAudioLevel: (level: number) => void;
  setTranscript: (transcript: string) => void;
  clearTranscript: () => void;
}

export const useSpeechStore = create<SpeechState>((set, get) => ({
  // Initial state
  isSupported: false,
  isRecording: false,
  isPlaying: false,
  audioLevel: 0,
  currentTranscript: '',
  
  // Actions
  initializeSpeech: async () => {
    try {
      // Check if browser supports required APIs
      const hasGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
      const hasMediaRecorder = !!window.MediaRecorder;
      const hasAudioContext = !!(window.AudioContext || (window as any).webkitAudioContext);
      
      const isSupported = hasGetUserMedia && hasMediaRecorder && hasAudioContext;
      
      set({ isSupported });
      
      if (!isSupported) {
        console.warn('Speech APIs not fully supported in this browser');
      }
      
      return isSupported;
    } catch (error) {
      console.error('Failed to initialize speech services:', error);
      set({ isSupported: false });
      return false;
    }
  },
  
  startRecording: async () => {
    try {
      const { isSupported } = get();
      
      if (!isSupported) {
        throw new Error('Speech recording not supported');
      }
      
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        } 
      });
      
      set({ isRecording: true, audioLevel: 0 });
      
      // Set up audio level monitoring
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      
      microphone.connect(analyser);
      analyser.fftSize = 256;
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      
      const updateAudioLevel = () => {
        if (get().isRecording) {
          analyser.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
          set({ audioLevel: average });
          requestAnimationFrame(updateAudioLevel);
        } else {
          audioContext.close();
        }
      };
      
      updateAudioLevel();
      
      return stream;
    } catch (error) {
      console.error('Failed to start recording:', error);
      set({ isRecording: false });
      throw error;
    }
  },
  
  stopRecording: () => {
    set({ isRecording: false, audioLevel: 0 });
  },
  
  playAudio: async (audioData: string) => {
    try {
      set({ isPlaying: true });
      
      // Convert base64 to blob
      const binaryString = atob(audioData);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      const blob = new Blob([bytes], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(blob);
      
      const audio = new Audio(audioUrl);
      
      return new Promise<void>((resolve, reject) => {
        audio.onended = () => {
          set({ isPlaying: false });
          URL.revokeObjectURL(audioUrl);
          resolve();
        };
        
        audio.onerror = (error) => {
          set({ isPlaying: false });
          URL.revokeObjectURL(audioUrl);
          reject(error);
        };
        
        audio.play().catch(reject);
      });
    } catch (error) {
      console.error('Failed to play audio:', error);
      set({ isPlaying: false });
      throw error;
    }
  },
  
  stopAudio: () => {
    set({ isPlaying: false });
    
    // Stop any currently playing audio
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach(audio => {
      audio.pause();
      audio.currentTime = 0;
    });
  },
  
  setAudioLevel: (level: number) => {
    set({ audioLevel: Math.min(100, Math.max(0, level)) });
  },
  
  setTranscript: (transcript: string) => {
    set({ currentTranscript: transcript });
  },
  
  clearTranscript: () => {
    set({ currentTranscript: '' });
  }
}));
