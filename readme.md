# OMANI-Therapist-Voice

A comprehensive mental health support chatbot that communicates exclusively through voice in Omani Arabic dialect, providing culturally sensitive, therapeutic-grade conversations with real-time speech processing capabilities.

## Project Structure

```
omani-therapist-voice/
├── frontend/                 # Next.js React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── stores/        # Custom React hooks for store
│   │   ├── utils/         # Utility functions
│   │   └── app/           # React Page Layout
│   └── package.json
├── backend/                 # FastAPI Python application
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   ├── requirements.txt
│   └── main.py
└── docs/                   # Documentation
```

## Features

- **Real-time Voice Processing**: Audio capture, STT, and TTS in Omani Arabic
- **Dual-Model AI**: GPT-4o with Google Gemini fallback/validation
- **Cultural Sensitivity**: Gulf-specific mental health terminology
- **Therapeutic Techniques**: CBT adaptation and crisis intervention
- **Safety Protocols**: Suicide risk assessment and escalation
- **HIPAA Compliance**: Secure data handling and privacy protection

## Quick Start

1. Clone the repository
2. Set up environment variables


## Architecture

The system uses a microservices architecture with:
- **Frontend**: Next.js with WebRTC for audio capture
- **Backend**: FastAPI with async processing
- **AI Models**: OpenAI GPT-4o,Google Gemini
- **Speech Services**: OpenAI Services for STT/TTS
- **Database**: PostgreSQL for session storage

## Ethical Considerations

- Transparent AI disclosure
- Data privacy and anonymization
- Professional supervision integration
- Cultural competency validation
