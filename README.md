# 🤖 PrayogAI - AI Chatbot Platform

**Build and deploy intelligent chatbots in minutes without coding.**

PrayogAI is a low-code platform that lets you create AI-powered chatbots from documents or websites, then embed them on any website with a single line of code.

---

## ✨ Key Features

- 📄 **Document-Based Bots** - Upload PDFs, DOCX, TXT files
- 🌐 **Website Scraping Bots** - Scrape any website (with login support)
- 🤖 **Smart AI Responses** - Powered by Google Gemini via Groq
- 🎨 **Embeddable Widget** - Add to any website with one script tag
- 🔐 **User Authentication** - Secure multi-tenant system
- 📊 **Production Ready** - Error handling, rate limiting, monitoring

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account
- Qdrant cloud account
- Groq API key

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create `.env` file:
```env
GROQ_API_KEY=your_groq_key
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
```

Run server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html
```

View coverage: Open `backend/htmlcov/index.html`

---

## 📡 API Endpoints

### Health & Monitoring
- `GET /api/health` - Check system status
- `GET /metrics` - View performance metrics

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Sign in
- `POST /auth/logout` - Sign out

### Bots
- `GET /api/bots` - List user's bots
- `POST /api/upload` - Create bot from documents
- `POST /api/scrape` - Create bot from website
- `DELETE /api/bots/{bot_id}` - Delete bot
- `GET /api/bots/{bot_id}/documents` - View bot documents

### Chat
- `POST /api/chat` - Send message to bot

---

## 🏗️ Tech Stack

**Backend:**
- FastAPI (Python)
- Supabase (Database + Auth)
- Qdrant (Vector Database)
- SentenceTransformers (Embeddings)
- Groq API (LLM - Gemini 2.5 Flash)
- BeautifulSoup, Selenium, Playwright (Web Scraping)

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Router v7
- Framer Motion

**Infrastructure:**
- pytest (Testing)
- GitHub Actions (CI/CD ready)
- Docker support

---

## 🛠️ Production Features

✅ **Error Handling** - Centralized exception handling with custom error types  
✅ **Rate Limiting** - 60 req/min general, 20 req/min for chat  
✅ **Health Checks** - Monitor API, Qdrant, Supabase, Groq status  
✅ **Metrics** - Track requests, response times, error rates  
✅ **Testing** - 15+ automated tests with 70%+ coverage  
✅ **Logging** - Comprehensive request/response logging  

---

## 📊 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Error handling, config, monitoring
│   │   ├── models/        # Pydantic models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Helper functions
│   ├── tests/             # Automated tests
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── context/       # Auth context
│   │   └── lib/           # API client
│   └── package.json
│
├── .github/
│   └── workflows/         # CI/CD pipelines
│
└── implementation-docs/   # Development docs
```

---

## 🎯 How It Works

1. **User creates account** → Supabase handles auth
2. **Upload documents or provide website URL** → Documents processed and chunked
3. **Embeddings generated** → SentenceTransformers creates vectors
4. **Stored in Qdrant** → Vector database for semantic search
5. **User gets embed code** → One-line JavaScript snippet
6. **Chat queries** → Semantic search + LLM generates responses

---

## 🔐 Security

- JWT-based authentication
- Row-level security in Supabase
- Rate limiting per IP
- Input validation
- XSS protection in widget
- Secure credential handling

---

## 📚 Documentation

- `implementation-docs/` - Feature implementation details
- `CI-CD-SETUP.md` - GitHub Actions setup guide
- `backend/QUICK_START.md` - Backend setup guide
- `about.md` - Detailed project overview

---

## 🧪 Testing the Platform

### Manual Testing:
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Visit `http://localhost:8000/api/health`
3. View metrics: `http://localhost:8000/metrics`

### Automated Tests:
```bash
cd backend
pytest -v
```

---

## 🚧 Development Status

**Current Version:** 1.0.0 - Production Ready

**Completed:**
- ✅ Core chatbot functionality
- ✅ Document upload & processing
- ✅ Website scraping (with authentication)
- ✅ Embeddable widget
- ✅ User authentication
- ✅ Production features (error handling, monitoring, rate limiting)
- ✅ Automated testing

**Planned Features:**
- Conversation history
- Analytics dashboard
- Multi-language support
- Advanced widget customization

---

## 📝 License

This project is for educational and development purposes.

---

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

---

## 📧 Contact

For questions or issues, check the documentation in `implementation-docs/`

---

**Built with ❤️ using FastAPI, React, and modern AI technologies**
