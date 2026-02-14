# MedAI Frontend

Modern React-based frontend for MedAI Assistant application.

## Tech Stack

- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript
- **Styling:** TailwindCSS
- **Linting:** ESLint with TypeScript support
- **Formatting:** Prettier

## Project Structure

```
frontend/
├── app/                   # Next.js app directory (pages & layouts)
├── components/            # React components
│   ├── ConversationView/  # Chat interface components
│   ├── ReportView/        # Report display & export
│   ├── Dashboard/         # User dashboard components
│   └── Common/            # Shared components
├── services/              # API & utility services
│   ├── api.ts            # Backend API integration
│   ├── auth.ts           # Authentication utilities
│   └── storage.ts        # LocalStorage utilities
├── hooks/                # Custom React hooks
├── styles/               # Global styles & CSS
├── utils/                # Helper functions
├── public/               # Static assets
├── package.json          # Dependencies & scripts
└── tsconfig.json         # TypeScript configuration
```

## Installation

### Prerequisites
- Node.js 18+ and npm/yarn
- Backend running on `http://localhost:8000`

### Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment variables:**
```bash
cp .env.example .env.local
# Edit .env.local if needed
```

3. **Start development server:**
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view in browser.

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - Check TypeScript types

## Development Workflow

### Code Standards
- **Formatting:** Run `npm run format` before committing
- **Linting:** Ensure `npm run lint` passes
- **Type Safety:** Check `npm run type-check` passes

### Component Structure
All components follow this structure:
```typescript
'use client'; // If interactive

interface Props {
  // Props interface
}

export default function ComponentName({ ...props }: Props): JSX.Element {
  // Component implementation
  return <div>{/* JSX */}</div>;
}
```

### API Integration
Use services from `services/api.ts`:
```typescript
import { conversationAPI, authAPI, patientAPI } from '@/services/api';

// Example usage
const conversations = await conversationAPI.list();
const report = await conversationAPI.getReport(conversationId);
```

## Features (Milestone 2)

### Task 2.1: Project Setup ✅
- [x] Next.js project with TypeScript
- [x] TailwindCSS styling
- [x] ESLint & Prettier configuration
- [x] Environment variables setup
- [x] Project structure organized
- [x] Base components & services

### Task 2.2: Core Components (Next)
- [ ] ConversationView components
- [ ] MessageBubble component
- [ ] InputField component
- [ ] Real-time message display

### Task 2.3: Report Display (Next)
- [ ] ReportDisplay component
- [ ] PDF export functionality
- [ ] Report sharing features

### Task 2.4: User Dashboard (Next)
- [ ] PatientDashboard component
- [ ] Conversation history list
- [ ] Search & filter functionality

### Task 2.5: Authentication (Next)
- [ ] Login/logout flows
- [ ] User registration
- [ ] Token refresh mechanism

### Task 2.6: API Integration (Next)
- [ ] Full backend integration
- [ ] WebSocket for real-time updates
- [ ] Error handling & retries

### Task 2.7: Testing & QA (Next)
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E testing with Cypress

## Environment Variables

Required environment variables (`.env.local`):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=MedAI Assistant
NEXT_PUBLIC_AUTH_ENABLED=true
NEXT_PUBLIC_FEATURE_EXPORT_PDF=true
NEXT_PUBLIC_FEATURE_SHARE=true
NEXT_PUBLIC_FEATURE_HISTORY=true
```

## API Endpoints

The frontend communicates with FastAPI backend at `http://localhost:8000`:

- `POST /api/conversations` - Create new conversation
- `GET /api/conversations` - List all conversations
- `GET /api/conversations/{id}` - Get conversation details
- `POST /api/conversations/{id}/messages` - Add message to conversation
- `GET /api/conversations/{id}/report` - Get generated report

## Performance Optimization

- Image optimization with Next.js Image component
- Code splitting at page level
- CSS optimization with Tailwind
- Font optimization with Next.js fonts

## Troubleshooting

### Port 3000 already in use
```bash
npm run dev -- -p 3001
```

### Backend connection issues
Ensure backend is running: `uvicorn main:app --reload`

### Module not found errors
```bash
npm install
npm run type-check
```

## Contributing

1. Create feature branch: `git checkout -b feature/component-name`
2. Make changes and format: `npm run format`
3. Lint code: `npm run lint`
4. Type check: `npm run type-check`
5. Commit changes with clear message
6. Push and create pull request

## Production Deployment

### Build
```bash
npm run build
```

### Deploy
```bash
npm start
```

The application will be available at configured URL.

## License

MIT License - MedAI Assistant Project

## Support

For issues and feature requests, please contact the development team.
