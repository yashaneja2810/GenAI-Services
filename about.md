# PrayogAI - Low-Code AI Chatbot Building Platform

## Project Overview

PrayogAI is a comprehensive, low-code AI chatbot building platform that empowers users to create, deploy, and manage intelligent chatbots for their websites without writing a single line of code. The platform leverages cutting-edge AI technologies to provide a seamless experience for building both document-based (static) and website-scraped (dynamic) chatbots that can be embedded on any website using a simple JavaScript snippet.

## Problem Statement

Businesses and organizations face several challenges when implementing AI chatbots:

1. **Technical Barrier**: Traditional chatbot development requires significant programming knowledge, AI/ML expertise, and infrastructure setup
2. **Time-Consuming Integration**: Setting up RAG (Retrieval-Augmented Generation) systems, vector databases, and LLM integrations is complex
3. **Document Knowledge Management**: Converting business documents and website content into conversational AI is technically challenging
4. **Deployment Complexity**: Embedding chatbots on websites typically requires backend infrastructure and API management
5. **Cost of Custom Development**: Building custom chatbot solutions from scratch is expensive and time-intensive
6. **Authentication Challenges**: Scraping authenticated/login-protected websites for knowledge bases requires specialized tooling


## Solution

PrayogAI provides an end-to-end platform that solves these challenges:

- **Zero-Code Bot Creation**: Intuitive web interface for creating chatbots in minutes, not weeks
- **Dual Bot Creation Modes**: Support for both static (document-based) and dynamic (website-scraped) bots
- **Automated RAG Pipeline**: Built-in document processing, chunking, embedding, and vector storage
- **One-Script Deployment**: Deploy chatbots to any website with a single JavaScript snippet
- **Authenticated Website Scraping**: Advanced web scraping with login support for protected content
- **Real-time Testing**: Integrated chat widget for immediate bot testing before deployment
- **Multi-tenant Architecture**: User authentication and bot ownership management built-in

---

## Core Features

### 1. User Authentication & Management

**Features:**
- Secure user registration and login powered by Supabase authentication
- Session management with JWT tokens and HTTP-only cookies
- User-specific bot ownership and access control
- Automatic token refresh and session handling
- Protected routes and API endpoints

**Benefits:**
- Each user has isolated bot management
- Secure multi-tenant architecture
- Seamless authentication experience across platform


### 2. Static Bot Creation (Document-Based)

**Features:**
- Upload multiple PDF, DOCX, and TXT documents simultaneously
- Drag-and-drop file upload interface
- Real-time file processing status indicators
- Automatic text extraction from various document formats
- Document preview and management

**Document Processing Pipeline:**
1. File upload with validation (PDF, DOCX, TXT)
2. Text extraction using specialized parsers:
   - PDF: PyPDF2 for text extraction
   - DOCX: python-docx for structured document parsing
   - TXT: chardet for automatic encoding detection
3. Intelligent text chunking with overlap for context preservation
4. Batch embedding generation using SentenceTransformers
5. Vector storage in Qdrant with metadata

**Use Cases:**
- Customer support knowledge bases
- Product manuals and documentation
- Company policy documents
- Training materials and guides
- FAQ databases


### 3. Dynamic Bot Creation (Website Scraping)

**Features:**
- Automatic website crawling and content extraction
- Multi-page crawling with intelligent link discovery
- Support for both public and authenticated websites
- Three-tier scraping strategy for maximum compatibility:
  - Fast HTTP crawling for server-rendered sites
  - Playwright rendering for JavaScript-heavy SPAs
  - Selenium fallback for complex authentication flows
- Real-time scraping progress and statistics
- Page count and chunk count tracking

**Advanced Authentication Support:**
- **Public Website Scraping**: No login required, crawls public pages
- **Authenticated Website Scraping**: Supports login-protected content
  - Standard login (single-page email/password forms)
  - Multi-step login (email → next → password flows)
  - Role-based login (Student/Employee/Admin selection)
  - Cookie consent and popup dismissal
  - Secure credential handling (in-memory only, never stored)

**Scraping Intelligence:**
- Same-domain link following to stay within website boundaries
- Duplicate content detection and removal
- Noise removal (navigation, footers, scripts, styles)
- Structured text extraction with metadata preservation
- Page title and URL tracking for source attribution

**Use Cases:**
- Company website content bots
- Product catalog chatbots
- Blog and documentation bots
- Internal portal knowledge bases (with authentication)
- Educational platform assistants


### 4. AI-Powered Chat Engine (RAG)

**Retrieval-Augmented Generation Pipeline:**

**Embedding & Vector Storage:**
- Model: `all-MiniLM-L6-v2` (SentenceTransformers)
- Vector dimensions: 384
- Distance metric: Cosine similarity
- Batch processing for efficient embedding generation
- Automatic retry mechanisms for robust storage

**Intelligent Retrieval:**
- Multi-phase semantic search with adaptive thresholds
- Top-K retrieval (default: top 10 chunks)
- Context deduplication to avoid redundant information
- Score-based filtering for relevance
- Metadata-enriched search results (source URLs, page titles)

**Response Generation:**
- LLM: Google Gemini 2.5 Flash (via Groq API)
- Context-aware prompt engineering
- Strict response behavior rules
- Natural language formatting
- Markdown support for rich formatting
- Error handling with graceful fallbacks

**Optimization Features:**
- Batched embedding generation (64 texts per batch)
- Batched upsert operations (50 points per batch)
- Exponential backoff retry logic
- Connection pooling and timeout management
- Qdrant cloud compatibility with 120s timeout


### 5. Bot Management Dashboard

**Features:**
- Comprehensive bot listing with search and filtering
- Bot statistics and performance metrics
- Document management and inspection
- Chunk count and file size tracking
- Real-time bot status monitoring
- Quick actions: Test, Embed, Delete

**Bot Information Display:**
- Bot name and creation date
- Document count and total chunks
- Source attribution (files or website URLs)
- Bot ID for API access
- Ownership verification

**Document Viewer:**
- Grouped by filename or source URL
- File size and chunk count per document
- Preview text for each document
- Created timestamp tracking
- Metadata inspection


### 6. Integrated Chat Testing Widget

**Features:**
- Real-time chat interface for bot testing
- Message threading and conversation history
- Typing indicators during response generation
- Error handling with user-friendly messages
- Markdown rendering for rich responses
- Responsive design for various screen sizes

**Testing Capabilities:**
- Immediate bot testing after creation
- No deployment required for testing
- Full conversation context maintained
- Response time monitoring
- Error state visualization


### 7. Embeddable Widget Script

**One-Line Integration:**
```html
<script src="https://your-domain.com/widget/widget.js" 
        data-bot-id="your-bot-id" 
        data-company-name="Your Company"
        data-color="#2563eb">
</script>
```

**Widget Features:**

**Core Functionality:**
- Floating chat button with customizable color
- Expandable/collapsible chat window
- Message input with send button and Enter key support
- Real-time message threading
- Bot and user message differentiation

**Advanced Features:**
- **Theme Support**: Light/dark mode toggle with system preference detection
- **Draggable Interface**: Move chat window anywhere on screen
- **Resizable Window**: Three size options (small, medium, large)
- **Markdown Formatting**: 
  - Bold text (**bold**)
  - Bullet lists (- item)
  - Numbered lists (1. item)
- **XSS Protection**: Automatic HTML escaping for security
- **Responsive Design**: Adapts to various screen sizes

**Customization Options:**
- Custom brand colors
- Company name display
- Bot ID configuration
- Theme preferences
- Widget positioning

**Technical Implementation:**
- Pure vanilla JavaScript (no dependencies)
- Self-contained IIFE (Immediately Invoked Function Expression)
- No conflicts with existing page scripts
- Minimal performance impact
- Cross-browser compatible


### 8. Public API Access

**Chat API Endpoint:**
- **Endpoint**: `POST /api/chat`
- **Authentication**: Not required (public access by design)
- **Purpose**: Enable widget and external integrations

**Request Format:**
```json
{
  "bot_id": "your-bot-uuid",
  "query": "User's question"
}
```

**Response Format:**
```json
{
  "response": "AI-generated answer based on bot's knowledge base"
}
```

**Features:**
- CORS enabled for cross-origin requests
- Anonymous bot access for widgets
- Authenticated endpoint available for protected bots
- Rate limiting ready (configurable)
- Health check endpoint for monitoring


### 9. Health Monitoring & Diagnostics

**System Health Check:**
- API service status
- Qdrant vector database connectivity
- Collection count and status
- Real-time health endpoint (`/api/health`)

**Error Handling:**
- Graceful degradation on service failures
- Detailed error logging for debugging
- User-friendly error messages
- Automatic retry mechanisms
- Timeout management

---

## Technical Architecture

### Backend Stack

**Framework & Core:**
- **FastAPI**: Modern, high-performance Python web framework
- **Python 3.11**: Latest stable Python version
- **Uvicorn**: Lightning-fast ASGI server
- **Pydantic**: Data validation and settings management

**Authentication & Database:**
- **Supabase**: 
  - PostgreSQL database backend
  - Built-in authentication and authorization
  - Row-level security (RLS)
  - Real-time subscriptions capability
- **JWT**: Stateless token-based authentication
- **Python-JOSE**: JWT encoding/decoding


**AI & Machine Learning:**
- **Google Gemini 2.5 Flash**: Advanced language model for response generation (via Groq API)
- **Groq API**: Ultra-fast LLM inference
- **SentenceTransformers**: State-of-the-art text embedding
  - Model: `all-MiniLM-L6-v2` (384 dimensions)
- **PyTorch**: Deep learning framework backend
- **NumPy & SciPy**: Scientific computing
- **Scikit-learn**: Machine learning utilities
- **LangChain**: LLM application framework

**Vector Database:**
- **Qdrant**: High-performance vector similarity search engine
  - Cloud and self-hosted support
  - Cosine similarity distance metric
  - Batch operations for efficiency
  - Point-based retrieval
  - Metadata filtering capabilities

**Document Processing:**
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX document parsing
- **chardet**: Automatic character encoding detection
- **python-slugify**: URL-safe string generation
- **RecursiveCharacterTextSplitter**: Intelligent text chunking with overlap


**Web Scraping Stack:**
- **BeautifulSoup4**: HTML/XML parsing and extraction
- **aiohttp**: Asynchronous HTTP client for fast crawling
- **Selenium**: Browser automation for JavaScript-rendered sites
  - Headless Chrome support
  - Login automation
  - Dynamic content handling
- **Playwright**: Modern browser automation (fallback)
  - Network idle detection
  - JS execution support
- **Requests**: HTTP library for synchronous requests

**Infrastructure:**
- **Docker**: Containerization for Qdrant local deployment
- **Docker Compose**: Multi-container orchestration
- **python-dotenv**: Environment variable management
- **CORS Middleware**: Cross-origin resource sharing support

### Frontend Stack

**Core Framework:**
- **React 18**: Modern UI library with concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Next-generation frontend build tool
  - Hot Module Replacement (HMR)
  - Optimized production builds
  - Fast development server


**UI & Styling:**
- **Tailwind CSS**: Utility-first CSS framework
  - Custom configuration
  - Responsive design utilities
  - Typography plugin for rich text
- **PostCSS**: CSS transformation and optimization
- **Autoprefixer**: Automatic vendor prefix handling

**Routing & State:**
- **React Router DOM v7**: Client-side routing
  - Protected routes
  - Nested routing
  - Programmatic navigation
- **Context API**: Global state management
  - Authentication context
  - User session management

**UI Libraries:**
- **Framer Motion**: Animation and gesture library
  - Page transitions
  - Component animations
  - Smooth interactions
- **Lucide React**: Beautiful, consistent icon library
- **Recharts**: Composable charting library

**HTTP & API:**
- **Axios**: Promise-based HTTP client
  - Request/response interceptors
  - Automatic token injection
  - Error handling


**Development Tools:**
- **ESLint**: JavaScript/TypeScript linting
- **TypeScript ESLint**: TypeScript-specific linting rules
- **Globals**: Global identifier definitions
- **Vite Plugin React**: Official React plugin for Vite

### Deployment Infrastructure

**Backend Deployment:**
- **Render**: Cloud platform for backend hosting
  - Automatic deployments
  - Environment variable management
  - Custom build commands
- **Heroku Compatible**: Procfile support
- **Runtime**: Python 3.11

**Frontend Deployment:**
- **Vercel**: Optimized for Vite/React applications
  - Automatic CI/CD
  - Edge network distribution
  - SPA routing configuration
  - Environment variable injection

**Database & Vector Store:**
- **Supabase Cloud**: Managed PostgreSQL
- **Qdrant Cloud**: Managed vector database
  - Or self-hosted via Docker


---

## Platform Advantages

### For Business Users

1. **Zero Technical Knowledge Required**
   - Intuitive drag-and-drop interface
   - Visual bot creation workflow
   - No coding or AI expertise needed

2. **Rapid Deployment**
   - Create bots in minutes
   - Instant testing capabilities
   - One-line website integration

3. **Cost-Effective**
   - No need for dedicated development team
   - No infrastructure management
   - Pay-per-use AI model costs only

4. **Scalable Solution**
   - Cloud-based vector storage
   - Handles multiple bots per user
   - Automatic scaling with demand

5. **Versatile Use Cases**
   - Customer support automation
   - Internal knowledge bases
   - Product documentation
   - Educational content delivery


### For Developers

1. **Modern Tech Stack**
   - Latest frameworks and libraries
   - Type-safe development with TypeScript
   - Fast development with Vite HMR

2. **Clean Architecture**
   - Separation of concerns
   - Service-based design
   - Singleton patterns for resource management
   - Modular component structure

3. **Production-Ready Code**
   - Error handling and retry mechanisms
   - Logging and monitoring
   - Security best practices
   - CORS and authentication

4. **Extensible Design**
   - Easy to add new LLM providers
   - Pluggable embedding models
   - Customizable scraping strategies
   - API-first architecture

5. **Developer Experience**
   - Hot reload in development
   - Comprehensive error messages
   - Automated setup scripts
   - Docker support for local development


### Technical Advantages

1. **Efficient RAG Implementation**
   - Optimized chunking with overlap for context
   - Batch embedding generation for performance
   - Smart retrieval with adaptive thresholds
   - Deduplication for cleaner context

2. **Robust Scraping Engine**
   - Three-tier fallback strategy
   - Handles JavaScript-heavy sites
   - Authentication support with security
   - Intelligent noise filtering

3. **Vector Database Optimization**
   - Batched upsert operations (50 points/batch)
   - Exponential backoff retry logic
   - Connection pooling
   - Cloud and self-hosted support

4. **Security Features**
   - JWT-based authentication
   - Row-level security with Supabase
   - In-memory credential handling (never stored)
   - XSS protection in widget
   - CORS configuration

5. **Performance Optimizations**
   - Concurrent HTTP requests during crawling
   - Lazy loading of AI models
   - Efficient embedding generation
   - Optimized vector search


---

## System Workflow

### Static Bot Creation Flow

1. **User Authentication**
   - User logs in via Supabase authentication
   - JWT token stored in session storage
   - Token injected in API requests

2. **Bot Configuration**
   - User enters bot name
   - Uploads PDF/DOCX/TXT files (drag-drop or file picker)
   - Frontend validates file types

3. **Document Processing**
   - Files sent to backend via multipart form
   - Backend creates bot entry in Supabase
   - Each file processed:
     - Text extracted based on file type
     - Text split into chunks (1000 chars, 200 overlap)
     - Metadata attached (filename, size, user ID)

4. **Vector Storage**
   - Chunks embedded using SentenceTransformers
   - Batch embedding (64 texts per batch)
   - Vectors stored in Qdrant collection `bot_{bot_id}`
   - Batch upsert (50 points per batch)

5. **Widget Generation**
   - JavaScript snippet generated with bot ID
   - User receives embed code
   - Bot ready for testing and deployment


### Dynamic Bot Creation Flow

1. **User Input**
   - User provides bot name and website URL
   - Optional: Login credentials for authenticated sites
   - Optional: User role for role-based login

2. **Website Scraping**
   - Phase 1: HTTP crawl attempt (fast)
     - aiohttp concurrent requests
     - BeautifulSoup content extraction
     - Internal link discovery
   - Phase 2: Playwright fallback (if needed)
     - Browser rendering for SPAs
     - Network idle detection
   - Phase 3: Selenium fallback (if needed)
     - Headless Chrome automation
     - Login flow execution
     - Dynamic content extraction

3. **Content Processing**
   - HTML cleaned and text extracted
   - Noise removed (nav, footer, scripts)
   - Text chunked with metadata (source URL, page title)
   - Statistics tracked (pages scraped, chunks created)

4. **Bot Creation**
   - Bot entry created in Supabase
   - Chunks embedded and stored in Qdrant
   - Widget code generated
   - Credentials cleared from memory


### Chat Interaction Flow

1. **User Query**
   - User types message in widget or app
   - Query sent to `/api/chat` endpoint
   - Bot ID included in request

2. **Retrieval Phase**
   - Query embedded using SentenceTransformers
   - Vector search in Qdrant collection
   - Top 10 similar chunks retrieved
   - Results scored and filtered

3. **Context Building**
   - Top chunks deduplicated
   - Context assembled with metadata
   - Bot knowledge prepared for LLM

4. **Response Generation**
   - Groq API called with Gemini model
   - System prompt includes bot context
   - Temperature set to 0.2 for consistency
   - Response generated based on knowledge

5. **Response Delivery**
   - Answer formatted with markdown
   - Response sent back to widget
   - Conversation history maintained


---

## Security Considerations

### Authentication Security
- JWT tokens with configurable expiration
- HTTP-only cookies for session management
- Bearer token authentication for APIs
- Row-level security in Supabase

### Data Security
- User bot ownership verification on every request
- Isolated vector collections per bot
- Secure credential handling (never logged or stored)
- CORS properly configured for production

### Widget Security
- XSS protection with HTML escaping
- Content Security Policy ready
- No inline script execution
- Sanitized user inputs

### API Security
- Rate limiting capability (configurable)
- Public endpoints clearly separated
- Authentication required for sensitive operations
- Error messages don't leak system information


---

## Use Cases & Applications

### 1. E-commerce Customer Support
- Product catalog knowledge base
- Order status inquiries
- Return and refund policies
- Size guides and specifications

### 2. Educational Institutions
- Course material assistance
- Admission information
- Campus facilities and services
- Student portal navigation (with authentication)

### 3. Corporate Internal Knowledge
- HR policies and procedures
- IT helpdesk automation
- Onboarding documentation
- Company wiki assistant

### 4. Healthcare & Medical
- Patient FAQ automation
- Appointment scheduling information
- Medical procedures explanation
- Insurance and billing queries

### 5. SaaS Product Documentation
- API documentation assistant
- Feature guides and tutorials
- Troubleshooting support
- Integration help

### 6. Real Estate
- Property listing information
- Neighborhood details
- Financing options
- Viewing appointment assistance

### 7. Legal & Compliance
- Policy document navigation
- Compliance requirement queries
- Legal document search
- Regulation interpretation


---

## Future Enhancement Opportunities

### Platform Features
- Multi-language support for chatbots
- Voice input/output capabilities
- Analytics dashboard with conversation insights
- A/B testing for bot responses
- Conversation history and export
- Custom branding and white-labeling
- Team collaboration features
- Bot templates for common use cases

### Technical Enhancements
- Support for additional document formats (Excel, CSV, PowerPoint)
- Image and table extraction from documents
- Multiple LLM provider support (OpenAI, Anthropic, etc.)
- Custom embedding model selection
- Fine-tuning capabilities
- Webhook integrations
- REST API for programmatic bot management
- GraphQL API option

### Widget Improvements
- Mobile-optimized interface
- Voice message support
- File upload in chat
- Rich media responses (images, videos)
- Suggested questions
- Conversation rating and feedback
- Multiple language support
- Offline mode with cached responses

### Scraping Enhancements
- Scheduled re-scraping for content updates
- Incremental scraping (only changed pages)
- API-based content ingestion
- Database direct connection
- Social media content scraping
- Video transcript extraction
- Audio file transcription

