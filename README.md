# Activewear Manufacturer Research Agent

An AI-powered platform for finding and evaluating activewear manufacturers. Available as both a **CLI tool** and a **full-stack web application** with authentication, database persistence, and real-time search tracking.

## Overview

This application uses Claude AI to intelligently research activewear manufacturers based on custom search criteria. It generates optimized search queries, scrapes manufacturer websites, extracts key information, and scores each manufacturer against your requirements.

### Two Ways to Use

1. **CLI Agent** - Standalone Python script for quick manufacturer research
2. **Web Application** - Full-stack platform with user authentication, search history, and persistent data

## Features

### Core Features (Both CLI & Web)
- **Intelligent Query Generation**: 7-10 strategically diverse search queries using industry terminology
- **Web Search Integration**: Brave Search API for finding manufacturer websites
- **Smart Web Scraping**: Automated extraction of manufacturer information
- **AI-Powered Evaluation**: Claude-based scoring system (0-100) against your criteria
- **Excel Export**: Formatted, ranked results with match scores

### Web Application Features
- **User Authentication**: JWT-based secure login/registration
- **Search History**: Track and review all past searches
- **Database Persistence**: PostgreSQL storage for searches and manufacturers
- **Real-time Progress**: Live updates as searches execute
- **Favorites & Notes**: Save and annotate promising manufacturers
- **Advanced Filtering**: Sort and filter results by score, location, certifications
- **Modern UI**: Next.js 16 with Tailwind CSS and Radix UI components

## Tech Stack

### CLI Agent
- **Language**: Python 3.12+
- **AI**: Anthropic Claude API
- **Web Search**: Brave Search API
- **Web Scraping**: BeautifulSoup4, httpx
- **Data Models**: Pydantic v2
- **Console UI**: Rich
- **Export**: openpyxl (Excel)

### Web Application
- **Backend**: FastAPI, SQLAlchemy (async), Alembic (migrations)
- **Frontend**: Next.js 16, React 19, TypeScript
- **Database**: PostgreSQL
- **Styling**: Tailwind CSS v4
- **UI Components**: Radix UI, shadcn-style
- **State Management**: Zustand (auth), TanStack Query (server state)
- **Deployment**: Railway (backend), Vercel (frontend)

---

## Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 20+** (for web app)
- **PostgreSQL** (for web app)
- **Anthropic API key** - [Get one here](https://console.anthropic.com/)
- **Brave Search API key** - [Free tier: 2,000 queries/month](https://brave.com/search/api/)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd activewear-agent

# Install CLI dependencies
pip install -r requirements.txt

# Install backend dependencies (for web app)
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies (for web app)
cd frontend
npm install
cd ..
```

### Configuration

#### 1. Root `.env` (for CLI agent)

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here
BRAVE_API_KEY=BSA-your-key-here

# Optional
REQUEST_DELAY_SECONDS=2
SCRAPE_TIMEOUT_SECONDS=30
MAX_MANUFACTURERS=10
```

#### 2. Backend `.env` (for web app)

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```bash
# Database (use docker-compose PostgreSQL locally)
DATABASE_URL=postgresql+asyncpg://agent_user:agent_password@localhost:5432/manufacturer_agent

# Auth (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
BRAVE_API_KEY=BSA-your-key-here

# CORS (adjust for production)
CORS_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=development
```

#### 3. Frontend `.env.local` (for web app)

```bash
cp frontend/.env.local.example frontend/.env.local
```

Edit `frontend/.env.local`:
```bash
# Local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production (set in Vercel dashboard)
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Running the CLI Agent

The CLI agent is perfect for quick, one-off manufacturer searches without needing to run the full web application.

### Basic Usage

```bash
# Activate the virtual environment (if not already active)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the agent
PYTHONPATH="$PWD/src:$PWD" python main.py
```

### What Happens

1. **Criteria Collection** - Interactive Q&A to gather your requirements
2. **Query Generation** - Claude generates 7-10 strategic search queries
3. **Web Search** - Brave Search finds manufacturer websites
4. **Scraping** - Extracts content from up to 10 websites
5. **Data Extraction** - Claude extracts structured data
6. **Evaluation** - Scores each manufacturer (0-100)
7. **Excel Export** - Saves results to `output/manufacturers_YYYY-MM-DD_HH-MM-SS.xlsx`

### Using Presets

Save frequently used search criteria:

```bash
# The agent will prompt you to save criteria as a preset
# Presets are saved in config/presets/

# Load a preset on next run by selecting "Load preset" option
```

### Example Search

When prompted, try these criteria:

```
Locations: USA, Vietnam
MOQ Range: 500 to 2000 units
Required Certifications: OEKO-TEX
Materials: recycled polyester, organic cotton
Production Methods: sublimation printing
Budget Tier: mid-range
```

---

## Running the Web App Locally

The web app provides a full-featured interface with authentication, search history, and persistent storage.

### Step 1: Start PostgreSQL

Using Docker Compose (recommended):

```bash
# Start PostgreSQL
docker-compose up -d

# Verify it's running
docker ps
```

Or install PostgreSQL manually and create the database:

```sql
CREATE DATABASE manufacturer_agent;
CREATE USER agent_user WITH PASSWORD 'agent_password';
GRANT ALL PRIVILEGES ON DATABASE manufacturer_agent TO agent_user;
```

### Step 2: Run Database Migrations

```bash
cd backend
source .venv/bin/activate  # Activate backend virtual environment
alembic upgrade head
```

### Step 3: Start the Backend

```bash
# From the backend directory
uvicorn app.main:app --reload

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Step 4: Start the Frontend

```bash
# Open a new terminal
cd frontend
npm run dev

# Frontend will be available at http://localhost:3000
```

### Step 5: Use the Application

1. Open http://localhost:3000
2. **Register** a new account
3. **Create a search** with your criteria
4. **Monitor progress** in real-time
5. **View results** with sorting and filtering
6. **Favorite** promising manufacturers
7. **Add notes** for future reference

---

## Connecting to the Database

### Local Database Connection

#### Using psql (PostgreSQL CLI)

```bash
# Connect to local database
psql -h localhost -U agent_user -d manufacturer_agent

# Common commands:
\dt              # List tables
\d users         # Describe users table
SELECT * FROM users;
SELECT * FROM searches LIMIT 5;
```

#### Using DBeaver, pgAdmin, or TablePlus

- **Host**: localhost
- **Port**: 5432
- **Database**: manufacturer_agent
- **Username**: agent_user
- **Password**: agent_password

#### Using Python

```python
import asyncpg

async def connect():
    conn = await asyncpg.connect(
        'postgresql://agent_user:agent_password@localhost:5432/manufacturer_agent'
    )
    rows = await conn.fetch('SELECT * FROM users')
    print(rows)
    await conn.close()
```

### Production Database Connection (Railway)

Railway auto-injects `DATABASE_URL` as an environment variable. To connect from your local machine:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link to project
railway login
railway link

# Get the database URL
railway variables

# Connect using psql
psql $DATABASE_URL
```

Or manually get the connection string from Railway dashboard:

1. Go to your Railway project
2. Click on the PostgreSQL service
3. Go to "Connect" tab
4. Copy the connection string
5. Use it to connect via psql, DBeaver, or any PostgreSQL client

---

## Deployment

### Backend Deployment (Railway)

Railway deployment is configured via `railway.toml` and `Dockerfile`.

#### Prerequisites

1. Create account at [Railway](https://railway.app/)
2. Install Railway CLI: `npm install -g @railway/cli`

#### Deploy

```bash
# Login to Railway
railway login

# Create new project (first time only)
railway init

# Add PostgreSQL service
railway add postgresql

# Deploy backend
railway up

# Set environment variables (via Railway dashboard or CLI)
railway variables set ANTHROPIC_API_KEY=sk-ant-xxx
railway variables set BRAVE_API_KEY=BSA-xxx
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set CORS_ORIGINS='["https://your-frontend.vercel.app"]'
railway variables set ENVIRONMENT=production
```

#### Environment Variables to Set

- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `BRAVE_API_KEY` - Your Brave Search API key
- `SECRET_KEY` - Random string for JWT signing (generate with Python command above)
- `CORS_ORIGINS` - JSON array of allowed frontend URLs
- `ENVIRONMENT` - Set to `production`
- `DATABASE_URL` - Auto-injected by Railway PostgreSQL plugin

#### Custom Domain (Optional)

1. Railway dashboard → Settings → Domains
2. Add custom domain or use Railway's generated domain
3. Update `CORS_ORIGINS` to include your frontend URL

#### Health Check

Railway uses `/api/health` endpoint (configured in `railway.toml`):

```bash
curl https://your-backend.railway.app/api/health
# Should return: {"status": "healthy"}
```

### Frontend Deployment (Vercel)

Vercel provides zero-config deployment for Next.js applications.

#### Prerequisites

1. Create account at [Vercel](https://vercel.com/)
2. Install Vercel CLI: `npm install -g vercel`

#### Deploy

```bash
cd frontend

# Login to Vercel
vercel login

# Deploy (first time)
vercel

# Follow prompts:
# - Link to existing project or create new
# - Select root directory: frontend/
# - Build command: npm run build
# - Output directory: .next

# Set environment variables in Vercel dashboard
# Project Settings → Environment Variables:
# NEXT_PUBLIC_API_URL = https://your-backend.railway.app
```

#### Environment Variables to Set

In Vercel dashboard (Settings → Environment Variables):

- `NEXT_PUBLIC_API_URL` - Your Railway backend URL (e.g., `https://your-app.railway.app`)

#### Production Deployment

```bash
# Deploy to production
vercel --prod
```

#### Custom Domain (Optional)

1. Vercel dashboard → Settings → Domains
2. Add custom domain
3. Update DNS records as instructed
4. Update backend `CORS_ORIGINS` to include your domain

### Post-Deployment Checklist

After deploying both services:

- [ ] Backend health check returns healthy: `curl https://your-backend.railway.app/api/health`
- [ ] Frontend loads: Visit your Vercel URL
- [ ] Registration works: Create a test account
- [ ] Login works: Sign in with test account
- [ ] Search works: Run a test search
- [ ] Backend CORS allows frontend domain (check `CORS_ORIGINS`)
- [ ] Database migrations ran successfully on Railway
- [ ] API keys are set in Railway environment variables
- [ ] Frontend `NEXT_PUBLIC_API_URL` points to Railway backend

---

## Project Structure

```
activewear-agent/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # pydantic-settings config
│   │   ├── database.py        # Async SQLAlchemy setup
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── search.py
│   │   │   ├── manufacturer.py
│   │   │   └── preset.py
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── api/               # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── presets.py
│   │   │   ├── search.py
│   │   │   └── manufacturers.py
│   │   ├── services/          # Business logic
│   │   │   ├── auth.py
│   │   │   └── agent_service.py  # Agent pipeline wrapper
│   │   └── core/
│   │       └── security.py    # JWT & password hashing
│   ├── alembic/               # Database migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── start.sh               # Production startup script
│   └── README.md
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router pages
│   │   │   ├── (auth)/        # Auth layout (login, signup)
│   │   │   ├── (dashboard)/   # Protected dashboard pages
│   │   │   ├── layout.tsx
│   │   │   └── providers.tsx
│   │   ├── components/
│   │   │   ├── ui/            # Base UI components
│   │   │   ├── auth/          # LoginForm, SignupForm
│   │   │   ├── search/        # CriteriaForm, SearchProgress
│   │   │   └── results/       # ManufacturerTable, ManufacturerCard
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # API client, utilities
│   │   ├── store/             # Zustand stores
│   │   └── types/             # TypeScript interfaces
│   ├── package.json
│   └── README.md
│
├── src/                        # CLI Agent source
│   ├── agent/                 # Agent orchestration
│   │   ├── core.py            # Main agent logic
│   │   ├── state.py           # State machine
│   │   └── prompts.py         # Claude prompts
│   ├── tools/                 # Individual capabilities
│   │   ├── criteria_collector.py
│   │   ├── query_generator.py
│   │   ├── web_searcher.py
│   │   ├── web_scraper.py
│   │   ├── data_extractor.py
│   │   ├── evaluator.py
│   │   └── excel_generator.py
│   ├── models/                # Data models
│   │   ├── criteria.py        # SearchCriteria model
│   │   └── manufacturer.py    # Manufacturer model
│   └── utils/                 # Utilities
│       └── llm.py             # Claude API wrapper
│
├── config/                     # Configuration
│   ├── settings.py            # Settings with defaults
│   └── presets/               # Saved criteria presets
│
├── output/                     # Generated Excel files
├── docker-compose.yml          # PostgreSQL for local development
├── Dockerfile                  # Backend production image
├── railway.toml                # Railway deployment config
├── main.py                     # CLI entry point
├── requirements.txt            # CLI agent dependencies
└── README.md                   # This file
```

---

## Search Criteria

The agent collects and evaluates manufacturers based on:

- **Locations** - Countries/regions (USA, China, Vietnam, Portugal, etc.)
- **MOQ Range** - Minimum and maximum order quantities
- **Certifications of Interest** - Certifications to look for (not strictly required)
- **Preferred Certifications** - Nice-to-have certifications
- **Materials** - Desired materials (recycled polyester, organic cotton, bamboo, etc.)
- **Production Methods** - Capabilities (sublimation, screen printing, cut-and-sew, etc.)
- **Budget Tier** - Can select multiple: budget, mid-range, premium
- **Additional Notes** - Any other requirements

---

## Scoring System

Manufacturers are scored on a 0-100 scale using a "reward what you find" philosophy:

### Location Match (25 points max)
- Exact location match: 25 pts
- Same region: 20 pts
- Trade partner country: 15 pts
- Location stated but not matched: 10 pts
- Unknown location: 5 pts

### MOQ Match (20 points max)
- Within range: 20 pts
- Close to range: 15 pts
- MOQ flexible/negotiable: 12 pts
- MOQ stated but not matched: 8 pts
- Unknown MOQ: 5 pts

### Certifications (25 points max)
- Per certification: +10 pts (capped at 25)
- Points awarded for certifications of interest found

### Materials (15 points max)
- Exact match: +5 pts per material
- Similar material: +3 pts
- Sustainable material bonus: +5 pts
- Premium material bonus: +3 pts
- Capped at 15 pts

### Production Methods (15 points max)
- Exact match: +5 pts per method
- Related method: +3 pts
- Full-service capability: +10 pts
- Capped at 15 pts

### Bonuses
- Has contact info: +5 pts
- High-quality website: +5 pts
- Website signals (e.g., "custom orders welcome"): variable points

**Final Score**: `min(100, max(0, base_score + bonuses))`

---

## API Endpoints

### Health
- `GET /api/health` - Health check

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get JWT token
- `GET /api/auth/me` - Current user info

### Criteria Presets
- `GET /api/presets` - List user's presets
- `POST /api/presets` - Create preset
- `GET /api/presets/{id}` - Get preset
- `PUT /api/presets/{id}` - Update preset
- `DELETE /api/presets/{id}` - Delete preset

### Search
- `POST /api/search/run` - Start search (async)
- `GET /api/search/{id}/status` - Poll progress
- `GET /api/search/{id}` - Full search details
- `GET /api/search/history` - User's search history
- `DELETE /api/search/{id}` - Delete search

### Manufacturers
- `GET /api/search/{search_id}/manufacturers` - List manufacturers (with sorting/filtering)
- `GET /api/manufacturers/{id}` - Get single manufacturer
- `PUT /api/manufacturers/{id}` - Update notes, tags, favorite status

---

## Configuration

### Environment Variables

#### CLI Agent (root `.env`)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx
BRAVE_API_KEY=BSA-xxx

# Optional
REQUEST_DELAY_SECONDS=2
SCRAPE_TIMEOUT_SECONDS=30
MAX_MANUFACTURERS=10
```

#### Backend (`backend/.env`)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname

# Auth
SECRET_KEY=random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxx
BRAVE_API_KEY=BSA-xxx

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=development  # or production
```

#### Frontend (`frontend/.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # or production URL
```

### Settings File

Edit [config/settings.py](config/settings.py) for advanced configuration:

```python
MAX_MANUFACTURERS: int = 10           # Max results per search
MAX_SEARCH_QUERIES: int = 5           # Number of search queries to execute
REQUEST_DELAY_SECONDS: float = 2.0    # Delay between web requests
SCRAPE_TIMEOUT_SECONDS: int = 30      # Timeout per website
BUDGET_LIMIT_USD: float = 50.0        # API spend limit
```

---

## Troubleshooting

### CLI Agent Issues

**"ANTHROPIC_API_KEY not found"**
- Create `.env` file from `.env.example`
- Ensure no quotes around the key

**"Brave API key invalid"**
- Check your key at [Brave API Dashboard](https://api.search.brave.com/app/dashboard)
- Ensure key starts with `BSA`

**Import errors when running main.py**
- Always set PYTHONPATH: `PYTHONPATH="$PWD/src:$PWD" python main.py`
- Or activate venv: `source venv/bin/activate`

**No manufacturers found**
- Try broader criteria (fewer certifications, more locations)
- Check your internet connection
- Verify Brave API quota hasn't been exceeded

### Web App Issues

**Backend won't start**
- Check PostgreSQL is running: `docker ps`
- Run migrations: `alembic upgrade head`
- Verify `DATABASE_URL` in `backend/.env`
- Check port 8000 isn't already in use

**Frontend can't connect to backend**
- Verify backend is running at http://localhost:8000
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Test backend health: `curl http://localhost:8000/api/health`
- Check for CORS errors in browser console

**Database connection errors**
- PostgreSQL not running: `docker-compose up -d`
- Wrong credentials in `DATABASE_URL`
- Database doesn't exist: Create it manually or check docker-compose

**Alembic migration errors**
- Reset database: `docker-compose down -v && docker-compose up -d`
- Delete alembic_version table if corrupted
- Run migrations: `alembic upgrade head`

**JWT authentication errors**
- Token expired: Login again
- Wrong `SECRET_KEY`: Regenerate and update backend
- `localStorage` cleared: Login again

### Deployment Issues

**Railway deployment fails**
- Check build logs in Railway dashboard
- Verify all environment variables are set
- Ensure `DATABASE_URL` is injected by PostgreSQL plugin
- Check `start.sh` has execute permissions

**Vercel deployment fails**
- Check build logs in Vercel dashboard
- Ensure `frontend/` is set as root directory
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- Check Next.js version compatibility

**CORS errors in production**
- Add frontend URL to backend `CORS_ORIGINS`
- Use full domain (https://your-app.vercel.app)
- Restart backend after changing CORS settings

---

## Development

### Running Tests

```bash
# Test imports (CLI agent)
python test_imports.py

# Test query generation
python test_query_generation.py

# Backend tests (if you create them)
cd backend
pytest tests/
```

### Creating Database Migrations

```bash
cd backend
source .venv/bin/activate

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column"

# Review the generated migration in alembic/versions/
# Edit if needed, then apply:
alembic upgrade head
```

### Adding New Search Criteria

1. Update [src/models/criteria.py](src/models/criteria.py) - Add field to `SearchCriteria`
2. Update [src/tools/criteria_collector.py](src/tools/criteria_collector.py) - Add collection logic
3. Update [src/tools/evaluator.py](src/tools/evaluator.py) - Add scoring logic
4. Update [backend/app/schemas/](backend/app/schemas/) - Add to API schemas
5. Update [frontend/src/types/](frontend/src/types/) - Add to TypeScript types
6. Update frontend form components

---

## Budget & Costs

### Estimated Costs Per Search

- **Query Generation**: ~$0.05
- **Data Extraction**: ~$0.50-1.00 (10 manufacturers)
- **Total per search**: ~$1-2

### API Limits

- **Brave Search**: 2,000 queries/month free (enough for ~400 searches)
- **Anthropic API**: Pay-as-you-go (typical $50 budget = 25-50 searches)

---

## Future Enhancements

- [ ] Support for additional data sources (Alibaba API, IndiaMART)
- [ ] Multi-page scraping (currently scrapes key pages only)
- [ ] Historical tracking (compare searches over time)
- [ ] Email outreach templates
- [ ] PDF export option
- [ ] Async scraping for better performance
- [ ] Image extraction (factory photos, product samples)
- [ ] Mobile app (React Native)
- [ ] Bulk manufacturer upload (CSV import)

---

## Documentation

- [README.md](README.md) - This file (complete guide)
- [QUICKSTART.md](QUICKSTART.md) - Quick setup for CLI agent
- [backend/README.md](backend/README.md) - Backend API documentation
- [frontend/README.md](frontend/README.md) - Frontend documentation
- [BRAVE_SEARCH_SETUP.md](BRAVE_SEARCH_SETUP.md) - Brave Search API setup guide
- [IMPLEMENTATION_IMPROVEMENTS.md](IMPLEMENTATION_IMPROVEMENTS.md) - Query generator improvements
- [QUERY_GENERATION_ANALYSIS.md](QUERY_GENERATION_ANALYSIS.md) - Query generation deep dive
- [QUERY_GENERATOR_SUMMARY.md](QUERY_GENERATOR_SUMMARY.md) - Query generator summary
- [BUDGET_TIER_FIX.md](BUDGET_TIER_FIX.md) - Budget tier validation fix
- [SAMPLE_URLS.md](SAMPLE_URLS.md) - Sample manufacturer URLs for testing

---

## Contributing

Contributions welcome! Areas for improvement:

- Better scraping logic (handle more website structures)
- Additional data sources (Alibaba, IndiaMART APIs)
- More sophisticated scoring algorithms
- UI/UX enhancements
- Mobile responsiveness improvements
- Test coverage

---

## License

MIT License - feel free to use and modify

---

## Support

For issues or questions:

1. Check the **Troubleshooting** section above
2. Review the relevant documentation file
3. Verify API keys and configuration
4. Check logs for error messages
5. Test with sample URLs from [SAMPLE_URLS.md](SAMPLE_URLS.md)

---

**Built with**:
- [Anthropic Claude API](https://www.anthropic.com/)
- [Brave Search API](https://brave.com/search/api/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [TailwindCSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)
