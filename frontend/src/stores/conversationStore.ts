import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  audio?: string;
  timestamp: Date;
  isAudio?: boolean;
  isError?: boolean;
  analysis?: {
    confidence: number;
    is_crisis: boolean;
    source: string;
    recommended_techniques: string;
    emotional_state: string;
    intent: string;
    crisis_assessment: {
      risk_level: string;
      indicators: string[];
      requires_intervention: boolean;
    };
    cultural_context: any;
  };
  culturalAdaptations?: string[];
}

export interface ConversationState {
  // State
  sessionId: string | null;
  messages: Message[];
  isConnected: boolean;
  isProcessing: boolean;
  
  // Actions
  initializeSession: () => Promise<void>;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  addConversation: () => void;
  endConversation: () => void;
  clearMessages: () => void;
  setConnectionStatus: (connected: boolean) => void;
  setProcessingStatus: (processing: boolean) => void;
  
  // WebSocket connection
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set, get) => ({
      // Initial state
      sessionId: null,
      messages: [],
      isConnected: false,
      isProcessing: false,
      
      // Actions
      initializeSession: async () => {
        try {
          // Lazy import to avoid store circular deps on server
          const { useLanguageStore } = await import('./languageStore');
          const selectedLanguage = useLanguageStore.getState().language;
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              language: selectedLanguage,
              cultural_context: {
                region: 'oman',
                dialect: 'omani',
                religious_sensitivity: true,
                family_orientation: true
              }
            }),
          });
          
          if (!response.ok) {
            throw new Error('Failed to create session');
          }
          
          const data = await response.json();
          
          set({
            sessionId: data.session_id,
            isConnected: true
          });
          
          // Initialize WebSocket connection
          get().connect();
          
        } catch (error) {
          console.error('Failed to initialize session:', error);
          set({ isConnected: false });
        }
      },
      
      addMessage: (message) => {
        const newMessage: Message = {
          ...message,
          id: Date.now().toString(),
          timestamp: new Date()
        };
        
        set((state) => ({
          messages: [...state.messages, newMessage]
        }));
      },
      
      clearMessages: () => {
        set({ messages: [] });
      },
      
      addConversation: () => {
        set({ messages: [] });
        get().disconnect();
        get().initializeSession();
      },
      endConversation: async () => {
        const session = get().sessionId;
        if (!session) return;
        set({ sessionId: null, messages: [] });
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/${session}/end`, {
            method: 'POST'})
        get().disconnect();
      },
      setConnectionStatus: (connected) => {
        set({ isConnected: connected });
      },
      
      setProcessingStatus: (processing) => {
        set({ isProcessing: processing });
      },
      
      // WebSocket methods
      connect: () => {
        const { sessionId } = get();
        if (!sessionId) return;
        
        const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WEBSOCKET_URL}?session=${sessionId}`);
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          set({ isConnected: true });
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        ws.onclose = () => {
          console.log('WebSocket disconnected');
          set({ isConnected: false });
          
          // Attempt to reconnect after 3 seconds
          setTimeout(() => {
            get().connect();
          }, 3000);
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          set({ isConnected: false });
        };
        
        // Store WebSocket reference for cleanup
        (get() as any).ws = ws;
      },
      
      disconnect: () => {
        const state = get() as any;
        if (state.ws) {
          state.ws.close();
          state.ws = null;
        }
        set({ isConnected: false });
      },
      
      sendMessage: (message) => {
        const state = get() as any;
        if (state.ws && state.ws.readyState === WebSocket.OPEN) {
          state.ws.send(JSON.stringify(message));
        }
      }
    }),
    {
      name: 'conversation-storage',
      partialize: (state) => ({
        sessionId: state.sessionId,
        messages: state.messages.slice(-50) // Keep only last 50 messages
      })
    }
  )
);

// WebSocket message handler
function handleWebSocketMessage(data: any) {
  const { addMessage, setProcessingStatus } = useConversationStore.getState();
  
  if (data.error) {
    // Handle error messages
    addMessage({
      type: 'assistant',
      content: 'عذراً، حدث خطأ في المعالجة. يرجى المحاولة مرة أخرى.',
      isError: true
    });
    setProcessingStatus(false);
    return;
  }
  
  if (data.response) {
    // Handle successful response
    addMessage({
      type: 'assistant',
      content: data.response.text,
      audio: data.response.audio,
      analysis: data.analysis,
      culturalAdaptations: data.response.cultural_adaptations,
      isAudio: true
    });
    setProcessingStatus(false);
  }
  
  if (data.transcript) {
    // Handle transcript updates
    // Could be used for real-time transcript display
    console.log('Transcript:', data.transcript);
  }
}
