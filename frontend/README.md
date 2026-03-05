# DNEXT Support Chatbot - Modern Frontend

A modern, professional React frontend for the DNEXT Support Chatbot with seamless light/dark mode support inspired by ChatGPT and Claude.

## Features

- **Modern UI Design**: Clean, professional interface with smooth animations and transitions
- **Perfect Dark Mode**: Automatic theme detection with manual override capability
- **Responsive Layout**: Mobile-first design with sidebar and chat interface
- **Real-time Chat**: Stream messages with loading indicators
- **Session Management**: Organize conversations by date
- **File Uploads**: Support for document uploads (integration pending)
- **User Authentication**: Simple email/name-based authentication
- **Type-Safe**: Full TypeScript support

## Tech Stack

- **Framework**: Next.js 16
- **UI Library**: React 19.2
- **Styling**: Tailwind CSS 3.4
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (Query)
- **Icons**: Lucide React
- **Theme**: next-themes
- **Language**: TypeScript

## Project Structure

```
frontend/
├── app/
│   ├── api/                 # API routes (proxy to Python backend)
│   │   ├── auth/login/
│   │   └── chat/send/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx            # Home page
│   └── globals.css         # Global styles
├── components/
│   ├── auth-modal.tsx       # Login form
│   ├── chat-layout.tsx      # Main layout wrapper
│   ├── chat-window.tsx      # Chat interface
│   ├── message-bubble.tsx   # Message component
│   ├── sidebar.tsx          # Conversation sidebar
│   └── theme-provider.tsx   # Theme provider
├── lib/
│   ├── store.ts           # Zustand stores (auth + chat)
│   └── utils.ts           # Utility functions
├── public/                # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── postcss.config.js
└── .env.example
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, pnpm, or bun

### Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   pnpm install
   # or
   yarn install
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env.local
   ```

4. **Configure API endpoint** (edit `.env.local`):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Development

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Color Scheme

### Light Mode
- **Background**: White (#ffffff)
- **Secondary Background**: Light Gray (#f8f9fa)
- **Text**: Dark Gray (#1a1a1a)
- **Border**: Light Gray (#e5e7eb)

### Dark Mode
- **Background**: Deep Blue-Black (#0f172a)
- **Secondary Background**: Slate (#1e293b)
- **Text**: Off White (#f1f5f9)
- **Border**: Dark Slate (#475569)

### Accent Colors
- **Primary**: Blue (#1e40af)
- **Secondary**: Cyan (#06b6d4)
- **Success**: Green (#10b981)

## API Integration

The frontend communicates with the Python backend through Next.js API routes:

### Authentication (`/api/auth/login`)
```json
Request:
{
  "email": "user@example.com",
  "name": "John Doe"
}

Response:
{
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Send Message (`/api/chat/send`)
```json
Request:
{
  "message": "Hello, how can I help?",
  "conversationId": "conv_123"
}

Response:
{
  "response": "AI response text..."
}
```

## Customization

### Theme Configuration

Edit `tailwind.config.ts` to customize colors and spacing:

```typescript
theme: {
  extend: {
    colors: {
      'accent-primary': '#your-color',
      // ... more colors
    },
  },
}
```

### Font Configuration

The project uses Inter from Google Fonts. To change:

1. Edit `app/layout.tsx`
2. Import different font from `next/font/google`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Optimized images with Next.js Image component
- Code splitting and lazy loading
- CSS-in-JS optimized builds
- Dark mode without layout shift

## Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- Proper heading hierarchy
- Color contrast compliance (WCAG AA)

## Deployment

### Vercel (Recommended)

```bash
vercel deploy
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Manual Deployment

1. Build: `npm run build`
2. Upload `/out` or run `npm start`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Python backend URL | `http://localhost:8000` |
| `NEXT_PUBLIC_DEFAULT_THEME` | Default theme | `system` |

## Troubleshooting

### Dark Mode Not Working
- Ensure `next-themes` is properly installed
- Check that `ThemeProvider` wraps your app
- Clear browser cache

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check Python backend is running
- Look for CORS errors in browser console

### Styling Issues
- Rebuild Tailwind: `npm run build`
- Clear Next.js cache: `rm -rf .next`

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, contact the development team.
