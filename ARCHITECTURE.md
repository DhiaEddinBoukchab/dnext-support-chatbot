# DNEXT Support Chatbot - Architecture Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                            │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Next.js Frontend (Port 3000)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  React Components                                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │AuthModal │  │ChatLayout│  │Sidebar   │  ...       │   │
│  │  └──────────┘  └──────────┘  └──────────┘             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                 │                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  State Management (Zustand)                             │   │
│  │  ├─ useAuthStore                                        │   │
│  │  └─ useChatStore                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                 │                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Styling (Tailwind CSS + globals.css)                   │   │
│  │  ├─ Light Mode: White bg, dark text                     │   │
│  │  └─ Dark Mode: Dark bg, light text                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP/REST API
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│            Next.js API Routes (Proxy Layer)                      │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ /api/auth/login  │  │/api/chat/send│  │/api/upload   │      │
│  └──────────────────┘  └──────────────┘  └──────────────┘      │
│                                 │                                │
│              Request validation & forwarding                     │
└─────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP/REST API
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│         Python Backend (Flask/FastAPI - Port 8000)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                           │  │
│  │  ├─ POST   /api/auth/login                              │  │
│  │  ├─ POST   /api/chat/send                               │  │
│  │  ├─ GET    /api/conversations                           │  │
│  │  ├─ GET    /api/conversation/{id}/messages              │  │
│  │  ├─ POST   /api/upload                                  │  │
│  │  ├─ DELETE /api/conversation/{id}                       │  │
│  │  └─ POST   /api/auth/logout                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                 │                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Core Services                                           │  │
│  │  ├─ Chatbot Engine                                       │  │
│  │  ├─ RAG System                                           │  │
│  │  ├─ Document Processor                                   │  │
│  │  ├─ Session Manager                                      │  │
│  │  └─ Authentication Service                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                 │                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Layer                                              │  │
│  │  ├─ User Database (PostgreSQL/SQLite)                    │  │
│  │  ├─ Vector DB (Chroma/Pinecone)                          │  │
│  │  ├─ Session Storage                                      │  │
│  │  └─ Conversation History                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
RootLayout
├── ThemeProvider (next-themes)
└── ChatLayout
    ├── AuthModal (if not authenticated)
    │   ├── Email input
    │   ├── Name input
    │   └── Sign In button
    │
    └── Main Layout (if authenticated)
        ├── Sidebar
        │   ├── New Chat Button
        │   ├── Conversation Groups
        │   │   ├── Today
        │   │   ├── Last 7 Days
        │   │   ├── Last 30 Days
        │   │   └── Older
        │   │       └── Conversation Items
        │   │           ├── Title
        │   │           ├── Date
        │   │           └── Delete Button
        │   ├── User Badge
        │   └── Sign Out Button
        │
        └── ChatWindow
            ├── Header
            │   ├── Title
            │   └── Settings Button
            ├── Messages Area
            │   └── MessageBubble (repeating)
            │       ├── User Message (blue)
            │       └── Bot Message (gray)
            └── Input Area
                ├── File Upload Button
                ├── Message Input
                └── Send Button
```

## Data Flow Diagram

### Authentication Flow

```
User → AuthModal Form
         ↓
      validation
         ↓
    POST /api/auth/login
         ↓
   Next.js API Route
         ↓
  POST /api/auth/login (Backend)
         ↓
   Authenticate User
    Create Session
         ↓
   Return User & Session
         ↓
  Update Zustand Store
    useAuthStore.setUser()
    useAuthStore.isAuthenticated = true
         ↓
   Redirect to ChatLayout
```

### Chat Flow

```
User → ChatWindow Input
         ↓
      Validate Message
         ↓
  addMessage(userMessage)
         ↓
    POST /api/chat/send
         ↓
   Next.js API Route
         ↓
  POST /api/chat/send (Backend)
         ↓
  Process with RAG Engine
  Generate Response
         ↓
   Return Response
         ↓
  addMessage(botMessage)
         ↓
  Display in MessageBubble
```

### Theme Flow

```
User Opens App
      ↓
ThemeProvider checks:
  ├─ localStorage (if saved preference)
  ├─ System preference (prefers-color-scheme)
  └─ Default (system)
      ↓
Set HTML class="light" or "dark"
      ↓
Tailwind CSS applies:
  ├─ Light mode rules
  └─ dark: prefixed rules
      ↓
Components render with correct colors
      ↓
User can toggle theme
      ↓
Update localStorage
      ↓
Re-render with new theme
```

## State Management

### useAuthStore (Zustand)

```typescript
interface AuthStore {
  user: User | null;              // Current logged-in user
  isAuthenticated: boolean;         // Auth state
  isLoading: boolean;               // Loading indicator
  login(email, name): Promise;      // Login user
  logout(): void;                   // Logout user
  setUser(user): void;              // Set user directly
}
```

### useChatStore (Zustand)

```typescript
interface ChatStore {
  conversations: Conversation[];    // List of conversations
  currentConversation: Conversation | null;  // Active chat
  messages: Message[];              // Messages in current chat
  isLoading: boolean;               // API loading state
  
  // Actions
  setConversations(convs);          // Update conversation list
  setCurrentConversation(conv);     // Switch active conversation
  setMessages(msgs);                // Set messages
  addMessage(msg);                  // Add single message
  setIsLoading(bool);               // Set loading state
  createConversation(title);        // Start new chat
  deleteConversation(id);           // Remove conversation
}
```

## API Contract

### Authentication Endpoint

**Request**: `POST /api/auth/login`

```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Response** (200 OK):

```json
{
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "avatar": "https://example.com/avatar.jpg"
  },
  "session_id": "session_123"
}
```

**Error Response** (400/500):

```json
{
  "error": "Email and name are required"
}
```

### Chat Endpoint

**Request**: `POST /api/chat/send`

```json
{
  "message": "What is your pricing?",
  "conversationId": "conv_123"
}
```

**Response** (200 OK):

```json
{
  "response": "Our pricing depends on your needs...",
  "conversationId": "conv_123",
  "messageId": "msg_456"
}
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Conversations Table

```sql
CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Messages Table

```sql
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL REFERENCES conversations(id),
  user_id TEXT NOT NULL REFERENCES users(id),
  role ENUM('user', 'assistant') NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Deployment Architecture

### Development

```
Developer Machine
├── Frontend: localhost:3000
├── Backend: localhost:8000
└── Database: SQLite/Local
```

### Production

```
CDN (Vercel Edge)
    ↓
Vercel (Frontend)
    ├── Static assets
    ├── API routes
    └── Incremental Static Regeneration
    
AWS/Railway/VPS (Backend)
    ├── Flask app
    ├── PostgreSQL
    ├── Vector DB (Chroma)
    └── File storage
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│      HTTPS/TLS Encryption               │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ↓                       ↓
   Frontend                  Backend
   ├─ Input validation     ├─ JWT authentication
   ├─ XSS protection       ├─ CORS validation
   └─ HTTPS only           ├─ SQL injection prevention
                           ├─ Rate limiting
                           └─ Session validation
```

## Performance Optimization

### Frontend

```
Next.js Optimizations:
├─ Code Splitting
├─ Automatic Image Optimization
├─ Dynamic Imports
├─ CSS-in-JS minification
├─ Tree shaking
└─ Minification

Browser:
├─ localStorage for user preference
├─ Service Workers (PWA ready)
├─ Lazy loading components
└─ Virtual scrolling (for long message lists)
```

### Backend

```
Python Optimizations:
├─ Connection pooling
├─ Query caching
├─ Async processing
├─ Batch operations
├─ Index optimization
└─ Response compression

Deployment:
├─ Gunicorn workers (4+)
├─ Load balancing
├─ CDN for static files
└─ Database replication
```

## Error Handling

### Frontend Error Flow

```
API Call
    ↓
Response Check
    ├─ Success (200) → Update UI
    ├─ Auth Error (401) → Redirect to login
    ├─ Not Found (404) → Show error message
    ├─ Server Error (500) → Show error message
    └─ Network Error → Show retry button
```

### Backend Error Flow

```
API Request
    ↓
Validate Input
    ├─ Invalid → Return 400
    ├─ Unauthorized → Return 401
    └─ Valid ↓
Process Request
    ├─ Database Error → Return 500
    ├─ Business Logic Error → Return 400
    └─ Success ↓
Return Response (200)
```

## Scaling Considerations

### Horizontal Scaling

```
Load Balancer
    ├─ Backend Instance 1
    ├─ Backend Instance 2
    ├─ Backend Instance 3
    └─ Backend Instance N
         ↓
    Shared Database
    Shared Vector DB
    Shared Session Store (Redis)
```

### Vertical Scaling

- Increase server resources
- Optimize database queries
- Cache frequently accessed data
- Use CDN for static assets

## Monitoring & Observability

```
Application
    ├─ Error Tracking (Sentry)
    ├─ Performance Monitoring (APM)
    ├─ Logging (Structured logs)
    ├─ Metrics (Prometheus)
    └─ Tracing (OpenTelemetry)
         ↓
    Dashboards (Grafana)
    Alerts (PagerDuty)
    Logs (ELK Stack)
```

## Technology Decision Rationale

| Decision | Alternative | Reason |
|----------|-------------|--------|
| Next.js | React SPA | Built-in API routes, SSR, better DX |
| Tailwind CSS | Bootstrap | Better dark mode, utility-first, smaller bundle |
| Zustand | Redux | Less boilerplate, easier to learn, perfect size |
| Flask | FastAPI | Familiar, simpler for MVP, can upgrade later |
| PostgreSQL | MongoDB | Structured data, relational integrity, ACID |
| Chroma | Pinecone | Open-source, self-hosted option, cost-effective |

## Future Architecture Improvements

1. **Microservices**
   - Separate auth, chat, document processing services
   - Independent scaling and deployment

2. **Message Queue**
   - RabbitMQ/Kafka for async processing
   - Better scalability for heavy workloads

3. **Caching Layer**
   - Redis for sessions and frequently accessed data
   - Improved response times

4. **API Gateway**
   - Rate limiting
   - Authentication
   - Request routing

5. **Admin Dashboard**
   - Analytics
   - User management
   - Content moderation

---

**Last Updated**: March 5, 2026
