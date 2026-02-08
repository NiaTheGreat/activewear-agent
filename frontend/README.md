# Manufacturer Agent Frontend

Next.js frontend for the AI-powered activewear manufacturer discovery platform.

## Prerequisites

- Node.js 20+ (recommended)
- Backend running at `http://localhost:8000`
- PostgreSQL + Redis via docker-compose

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4
- **UI Components**: Radix UI primitives (shadcn-style)
- **State**: Zustand (auth), TanStack React Query (server state)
- **Forms**: Controlled components with multi-select chips
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Notifications**: Sonner

## Project Structure

```
src/
├── app/                  # Next.js App Router pages
│   ├── (auth)/           # Auth layout (login, signup)
│   ├── (dashboard)/      # Dashboard layout (all protected pages)
│   ├── layout.tsx        # Root layout
│   └── providers.tsx     # QueryClient, Toaster, Tooltip providers
├── components/
│   ├── ui/               # Base UI components (button, input, card, etc.)
│   ├── auth/             # LoginForm, SignupForm
│   ├── layout/           # Navbar, Sidebar, PageTransition
│   ├── search/           # CriteriaForm, SearchProgress, PresetSelector
│   ├── results/          # ManufacturerTable, ManufacturerCard, ScoringBreakdown
│   └── common/           # LoadingSkeleton, EmptyState
├── hooks/                # useAuth, useSearch, useManufacturers, useLocalStorage
├── lib/                  # api.ts, utils.ts, constants.ts
├── store/                # Zustand auth store
└── types/                # TypeScript interfaces matching backend schemas
```

## Backend Integration

The frontend expects the FastAPI backend at the URL defined in `NEXT_PUBLIC_API_URL`.

### API Endpoints Used

| Category | Endpoint | Method |
|---|---|---|
| Auth | `/api/auth/register` | POST |
| Auth | `/api/auth/login` | POST |
| Auth | `/api/auth/me` | GET |
| Presets | `/api/presets` | GET, POST |
| Presets | `/api/presets/:id` | GET, PUT, DELETE |
| Search | `/api/search/run` | POST |
| Search | `/api/search/:id/status` | GET |
| Search | `/api/search/:id` | GET |
| Search | `/api/search/history` | GET |
| Search | `/api/search/:id` | DELETE |
| Manufacturers | `/api/search/:id/manufacturers` | GET |
| Manufacturers | `/api/manufacturers/:id` | GET, PUT |

### Authentication

JWT tokens are stored in `localStorage` under the key `token` and sent as `Authorization: Bearer {token}` headers.

## Available Scripts

```bash
npm run dev      # Start development server (port 3000)
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```
