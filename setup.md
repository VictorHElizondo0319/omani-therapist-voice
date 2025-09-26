# 🛠️ Setup Guide — Omani Voice Therapy Assistant

This project consists of:  
- **Frontend** → Next.js (React)  
- **Backend** → FastAPI (Python)  
- **Database** → PostgreSQL  

---

## 📦 1. Prerequisites
Make sure you have the following installed:

- **Node.js** → v20 or later  
- **Python** → v3.10 or later  
- **PostgreSQL** → v14 or later  

Check versions:
```bash
node -v
python --version
psql --version
```
## 📖 2. env setup

```bash

copy env.exmaple .env

OPENAI_API_KEY=your_openai_key
OPENAI_API_MODEL=your_openai_model
GOOGLE_API_KEY=your_gemini_key
GOOGLE_AI_MODEL=your_gomini_model
DATABASE_URL=your_postgresql_databse_uri


```

## 🎨 3. Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev

# http://localhost:3000
```

## ⚙️ 4. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows

pip install -r requirements.txt
python main.py

# http://localhost:8000
```
