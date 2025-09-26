# OMANI-Therapist-Voice Architecture

## System Overview

The OMANI-Therapist-Voice system is a comprehensive mental health support chatbot designed specifically for Omani Arabic speakers. It provides real-time voice-based conversations with culturally sensitive therapeutic responses.

## Architecture Components

### 1. Frontend (Next.js)
- **Technology**: Next.js 14 with TypeScript
- **UI Framework**: Tailwind CSS with custom Arabic styling
- **State Management**: Zustand for global state
- **Real-time Communication**: WebSocket connections
- **Audio Processing**: WebRTC for audio capture and playback

### 2. Backend (FastAPI)
- **Technology**: FastAPI with Python 3.11
- **Database**: PostgreSQL with SQLAlchemy ORM

#TODO
### 3. AI Services
- **Primary Model**: OpenAI GPT-4o
- **Fallback Model**: Anthropic Claude Opus 4
- **Speech Services**: OpenAI GPT-4o
- **Dual-Model Strategy**: 

### 4. Data Layer
- **PostgreSQL**: Main database for conversation storage
- **File Storage**: Encrypted audio file storage

## Data Flow Architecture

```
User Voice Input → Frontend Audio Capture → Backend Processing
                                                          ↓
AI STT → Therapy Analysis → AI Response Generation → Cultural Adaptation
                                                          ↓
TTS Synthesis  →    Frontend Audio Playback     →       User
```

## Security Architecture

### 1. Data Encryption
- **In Transit**: TLS 1.3 for all communications
- **At Rest**: AES-256 encryption for sensitive data
- **Audio Data**: Encrypted storage with minimal retention

## Cultural Adaptation Layer

### 1. Omani Arabic Dialect Processing
- **STT Optimization**: Custom models for Omani dialect
- **Cultural Context**: Islamic values and family dynamics
- **Terminology**: Mental health vocabulary in Arabic
- **Code-switching**: Arabic-English mixing support

### 2. Therapeutic Techniques
- **CBT Adaptation**: Cognitive Behavioral Therapy in Arabic context
- **Crisis Intervention**: Automated risk assessment and escalation
- **Cultural Sensitivity**: Religious and social norm awareness
- **Emotional Intelligence**: Nuanced emotional state detection

## Performance Optimization

### 1. Latency Targets
- **End-to-end Response**: < 20 seconds per conversation turn
- **Audio Processing**: < 5 seconds for STT/TTS
- **AI Response**: < 10 seconds for dual-model generation

### 2. Scalability Features
- **Database Optimization**: Connection pooling and indexing

## Monitoring & Observability

### 1. Health Checks
- **Service Health**: Automated health monitoring
- **Performance Metrics**: Response time and throughput
- **Error Tracking**: Comprehensive error logging

### 2. Analytics
- **Usage Analytics**: Conversation patterns and effectiveness
- **Cultural Metrics**: Adaptation usage and accuracy
- **Safety Metrics**: Crisis intervention statistics
- **Performance Metrics**: System performance and reliability

## Deployment Architecture

### 1. Container Orchestration
- **Docker**: Containerized services
- **Docker Compose**: Local development and testing
- **Production**: Kubernetes-ready configuration

### 2. Infrastructure
- **Web Server**: Nginx reverse proxy
- **Database**: PostgreSQL with backup strategy

## API Design

### 1. RESTful APIs
- **Conversation Management**: Session creation and management
- **Analysis Endpoints**: Emotional and cultural analysis
- **Response Generation**: AI response creation
- **Safety Protocols**: Crisis intervention and escalation

### 2. WebSocket APIs
- **Real-time Audio**: Bidirectional audio streaming
- **Live Transcription**: Real-time speech-to-text
- **Status Updates**: Connection and processing status

## Data Models

### 1. Core Entities
- **ConversationSession**: Main conversation container
- **ConversationTurn**: Individual conversation exchanges
- **SafetyIncident**: Crisis and safety-related events
- **CulturalAdaptation**: Cultural context and adaptations

## Future Enhancements

### 1. Advanced AI Features
- **Multi-modal Input**: Text, voice, and emotion recognition
- **Personalization**: User-specific adaptation
- **Learning**: Continuous improvement from interactions

### 2. Expanded Cultural Support
- **Regional Dialects**: Support for other Gulf dialects
- **Multilingual**: Additional language support
- **Cultural Customization**: User-specific cultural preferences

### 3. Clinical Integration
- **Professional Dashboard**: Therapist monitoring interface
- **Session Notes**: Automated session documentation
- **Referral System**: Integration with healthcare providers

## Compliance & Ethics

### 1. Regulatory Compliance
- **HIPAA**: Healthcare data protection
- **GDPR**: European data protection (if applicable)
- **Local Regulations**: Omani healthcare regulations

### 2. Ethical Considerations
- **Transparency**: Clear AI disclosure to users
- **Bias Prevention**: Regular bias testing and mitigation
- **User Consent**: Informed consent for data processing
- **Professional Oversight**: Clinical supervision integration