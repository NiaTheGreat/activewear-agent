# Production Deployment Guide

Complete guide for deploying the Activewear Agent application to production using **Railway** (backend) and **Vercel** (frontend).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Deployment (Railway)](#backend-deployment-railway)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Environment Variables](#environment-variables)
6. [Custom Domains](#custom-domains)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Monitoring & Logs](#monitoring--logs)
9. [CI/CD Setup](#cicd-setup)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)

---

## Architecture Overview

### Production Stack

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Vercel)                          │
│  • Next.js 16 App Router                                    │
│  • Static + Server-Side Rendering                           │
│  • Auto-scaling, Global CDN                                 │
│  • Domain: your-app.vercel.app                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Railway)                          │
│  • FastAPI + Uvicorn                                        │
│  • Auto-deployed from GitHub/Git                            │
│  • Automatic migrations on deploy                           │
│  • Domain: your-backend.railway.app                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL (Railway Plugin)                   │
│  • Managed PostgreSQL 15                                    │
│  • Automatic backups                                        │
│  • DATABASE_URL auto-injected                               │
└─────────────────────────────────────────────────────────────┘
```

### Why Railway + Vercel?

**Railway (Backend)**:
- ✅ Free $5/month credit (enough for hobby projects)
- ✅ Automatic deployments from Git
- ✅ Built-in PostgreSQL plugin
- ✅ Environment variable management
- ✅ Easy domain management

**Vercel (Frontend)**:
- ✅ Free for hobby projects (unlimited bandwidth)
- ✅ Zero-config Next.js deployment
- ✅ Global CDN (fast worldwide)
- ✅ Automatic HTTPS
- ✅ Preview deployments for PRs

---

## Prerequisites

### Required Accounts

1. **Railway Account** - [Sign up](https://railway.app/)
   - Free $5/month credit
   - Credit card optional for additional credits

2. **Vercel Account** - [Sign up](https://vercel.com/)
   - Free tier (hobby)
   - No credit card required

3. **GitHub Account** (Recommended)
   - For automatic deployments
   - CI/CD integration

### Required Tools

Install these on your local machine:

```bash
# Railway CLI
npm install -g @railway/cli

# Vercel CLI
npm install -g vercel

# Git (if not already installed)
git --version
```

### Required API Keys

Before deployment, obtain:

1. **Anthropic API Key** - [Get one here](https://console.anthropic.com/)
2. **Brave Search API Key** - [Get one here](https://brave.com/search/api/)

---

## Backend Deployment (Railway)

### Step 1: Create Railway Account

1. Go to [Railway.app](https://railway.app/)
2. Click **"Start a New Project"** or **"Login"** (if you have an account)
3. Sign up with GitHub (recommended) or email
4. Verify your email

### Step 2: Install Railway CLI

```bash
# Install globally
npm install -g @railway/cli

# Verify installation
railway --version

# Login to Railway
railway login
```

This opens a browser for authentication. Complete the login process.

### Step 3: Initialize Railway Project

From your project root directory:

```bash
# Initialize Railway project
railway init

# You'll be prompted:
# - Project name: "activewear-agent" (or your preferred name)
# - Environment: "production"

# Link to the project
railway link
```

**Alternative**: Create project via Railway Dashboard
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"** (if using GitHub)
4. Authorize Railway to access your GitHub
5. Select your repository

### Step 4: Add PostgreSQL Database

```bash
# Add PostgreSQL plugin
railway add postgresql

# Wait for provisioning (30-60 seconds)
```

**Or via Dashboard**:
1. Open your project in Railway Dashboard
2. Click **"+ New"**
3. Select **"Database"** → **"PostgreSQL"**
4. Wait for provisioning

**Important**: Railway automatically creates and injects `DATABASE_URL` as an environment variable.

### Step 5: Configure Environment Variables

```bash
# Set environment variables via CLI
railway variables set ANTHROPIC_API_KEY="sk-ant-your-key-here"
railway variables set BRAVE_API_KEY="BSA-your-key-here"
railway variables set ENVIRONMENT="production"

# Generate and set SECRET_KEY
railway variables set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Set CORS origins (update after deploying frontend)
railway variables set CORS_ORIGINS='["https://your-frontend.vercel.app"]'

# Set JWT algorithm
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="1440"
```

**Or via Dashboard**:
1. Open project in Railway Dashboard
2. Select your service
3. Go to **"Variables"** tab
4. Click **"+ New Variable"**
5. Add each variable:
   - `ANTHROPIC_API_KEY` = `sk-ant-xxx`
   - `BRAVE_API_KEY` = `BSA-xxx`
   - `SECRET_KEY` = (generate with Python command above)
   - `CORS_ORIGINS` = `["https://your-frontend.vercel.app"]`
   - `ENVIRONMENT` = `production`
   - `ALGORITHM` = `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` = `1440`

### Step 6: Deploy Backend

Railway automatically deploys from your [Dockerfile](Dockerfile):

```bash
# Deploy current code
railway up

# Or if using GitHub integration:
git push origin main  # Railway auto-deploys on push
```

**Deployment Process**:
1. Railway builds Docker image from [Dockerfile](Dockerfile)
2. Runs [backend/start.sh](backend/start.sh):
   - Executes database migrations (`alembic upgrade head`)
   - Starts FastAPI server (`uvicorn app.main:app`)
3. Exposes service on Railway subdomain

**Monitor Deployment**:
```bash
# View deployment logs
railway logs

# Or via Dashboard: Click service → "Deployments" tab
```

### Step 7: Get Backend URL

```bash
# Get your Railway domain
railway domain

# Output example: your-app-production-xxxxx.railway.app
```

**Or via Dashboard**:
1. Open project → Select service
2. Go to **"Settings"** tab
3. Scroll to **"Domains"**
4. Copy the generated domain: `your-app.railway.app`

### Step 8: Update CORS Origins

Now that you have the backend URL, you'll update CORS after deploying frontend. Keep this URL handy.

### Step 9: Verify Backend Deployment

Test the health endpoint:

```bash
# Replace with your Railway domain
curl https://your-app.railway.app/api/health

# Expected response:
# {"status":"healthy"}
```

Test API docs (if `ENVIRONMENT=development`):
- Visit: `https://your-app.railway.app/docs`

**Note**: API docs are disabled in production by default. To enable:
```bash
railway variables set ENVIRONMENT="development"
```

---

## Frontend Deployment (Vercel)

### Step 1: Create Vercel Account

1. Go to [Vercel.com](https://vercel.com/)
2. Click **"Sign Up"**
3. Sign up with GitHub (recommended)
4. Complete verification

### Step 2: Install Vercel CLI

```bash
# Install globally
npm install -g vercel

# Verify installation
vercel --version

# Login to Vercel
vercel login
```

### Step 3: Deploy Frontend

From your project root directory:

```bash
# Navigate to frontend directory
cd frontend

# Deploy to Vercel
vercel

# Follow prompts:
# - Set up and deploy: Y
# - Which scope: (your account)
# - Link to existing project: N
# - Project name: activewear-agent-frontend
# - Directory: ./
# - Override settings: N

# Wait for deployment (2-3 minutes)
```

**Initial Deployment Output**:
```
🔗 Deployed to production: https://activewear-agent-frontend.vercel.app
```

### Step 4: Set Environment Variables

**Via Vercel CLI**:
```bash
# Set production environment variable
vercel env add NEXT_PUBLIC_API_URL production

# When prompted, enter: https://your-app.railway.app
```

**Via Vercel Dashboard** (Recommended):
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **"Settings"** → **"Environment Variables"**
4. Add variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-app.railway.app` (your Railway backend URL)
   - **Environments**: Select **"Production"**, **"Preview"**, **"Development"**
5. Click **"Save"**

### Step 5: Redeploy with Environment Variable

```bash
# Redeploy to production
vercel --prod

# Wait for deployment
```

**Or via Dashboard**:
1. Go to **"Deployments"** tab
2. Find latest deployment
3. Click **"..."** menu → **"Redeploy"**

### Step 6: Get Frontend URL

Your frontend will be available at:
```
https://activewear-agent-frontend.vercel.app
```

Or your custom domain (if configured).

### Step 7: Update Backend CORS

Now update the backend to allow requests from your frontend:

```bash
# Update CORS_ORIGINS in Railway
railway variables set CORS_ORIGINS='["https://activewear-agent-frontend.vercel.app"]'

# Railway automatically redeploys when variables change
```

**Or via Railway Dashboard**:
1. Select backend service
2. Go to **"Variables"** tab
3. Edit `CORS_ORIGINS` variable
4. Update value: `["https://activewear-agent-frontend.vercel.app"]`
5. Click **"Update"**
6. Wait for automatic redeployment

### Step 8: Verify Frontend Deployment

Visit your frontend URL:
```
https://activewear-agent-frontend.vercel.app
```

You should see:
- ✅ Login/signup page loads
- ✅ No CORS errors in browser console (F12)
- ✅ Can register a new account
- ✅ Can login and access dashboard

---

## Environment Variables

### Backend (Railway)

Complete list of environment variables needed:

| Variable | Value | Required | Description |
|----------|-------|----------|-------------|
| `DATABASE_URL` | Auto-injected | ✅ Yes | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | `sk-ant-xxx` | ✅ Yes | Anthropic API key |
| `BRAVE_API_KEY` | `BSA-xxx` | ✅ Yes | Brave Search API key |
| `SECRET_KEY` | Random string | ✅ Yes | JWT signing key |
| `CORS_ORIGINS` | `["https://..."]` | ✅ Yes | Allowed frontend origins |
| `ENVIRONMENT` | `production` | ✅ Yes | Environment mode |
| `ALGORITHM` | `HS256` | ⚠️ Optional | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | ⚠️ Optional | Token expiry (default: 1440) |

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend (Vercel)

| Variable | Value | Required | Description |
|----------|-------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://your-app.railway.app` | ✅ Yes | Backend API URL |

**Important**: Must start with `NEXT_PUBLIC_` to be exposed to the browser.

---

## Custom Domains

### Backend Custom Domain (Railway)

#### Option 1: Railway Subdomain

Railway provides a free `.railway.app` subdomain automatically.

#### Option 2: Custom Domain

1. **Add Domain in Railway**:
   - Open project → Select backend service
   - Go to **"Settings"** → **"Domains"**
   - Click **"Add Domain"**
   - Enter: `api.yourdomain.com`

2. **Configure DNS**:
   Add CNAME record in your DNS provider:
   ```
   Type: CNAME
   Name: api (or your subdomain)
   Value: your-app.railway.app
   TTL: 3600
   ```

3. **Wait for Verification** (5-30 minutes)

4. **Update CORS**:
   ```bash
   railway variables set CORS_ORIGINS='["https://yourdomain.com"]'
   ```

### Frontend Custom Domain (Vercel)

#### Option 1: Vercel Subdomain

Vercel provides a free `.vercel.app` subdomain automatically.

#### Option 2: Custom Domain

1. **Add Domain in Vercel**:
   - Open project in Vercel Dashboard
   - Go to **"Settings"** → **"Domains"**
   - Click **"Add"**
   - Enter: `yourdomain.com` or `www.yourdomain.com`

2. **Configure DNS**:

   **For apex domain** (yourdomain.com):
   ```
   Type: A
   Name: @
   Value: 76.76.21.21
   ```

   **For www subdomain**:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

3. **Verify in Vercel** (click "Verify")

4. **Update Backend CORS**:
   ```bash
   railway variables set CORS_ORIGINS='["https://yourdomain.com","https://www.yourdomain.com"]'
   ```

---

## Post-Deployment Verification

### Automated Verification Script

Create [scripts/verify-deployment.sh](scripts/verify-deployment.sh):

```bash
#!/bin/bash

# Configuration
BACKEND_URL="https://your-app.railway.app"
FRONTEND_URL="https://your-app.vercel.app"

echo "🔍 Verifying deployment..."

# 1. Backend health check
echo "1. Checking backend health..."
HEALTH=$(curl -s "$BACKEND_URL/api/health")
if [[ $HEALTH == *"healthy"* ]]; then
  echo "   ✅ Backend is healthy"
else
  echo "   ❌ Backend health check failed"
  exit 1
fi

# 2. Backend API docs (if enabled)
echo "2. Checking API docs..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs")
if [[ $STATUS == "200" || $STATUS == "404" ]]; then
  echo "   ✅ Backend is responding"
else
  echo "   ⚠️  Backend may have issues (Status: $STATUS)"
fi

# 3. Frontend loads
echo "3. Checking frontend..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [[ $STATUS == "200" ]]; then
  echo "   ✅ Frontend is accessible"
else
  echo "   ❌ Frontend not accessible (Status: $STATUS)"
  exit 1
fi

# 4. Database connection (register test user)
echo "4. Testing database connection (registration)..."
REGISTER=$(curl -s -X POST "$BACKEND_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | grep -o "email")

if [[ $REGISTER == "email" ]]; then
  echo "   ✅ Database connection working"
else
  echo "   ⚠️  Could not verify database (user may already exist)"
fi

echo ""
echo "✨ Deployment verification complete!"
```

Run verification:
```bash
chmod +x scripts/verify-deployment.sh
./scripts/verify-deployment.sh
```

### Manual Verification Checklist

- [ ] **Backend Health**: `curl https://your-app.railway.app/api/health`
- [ ] **Frontend Loads**: Visit `https://your-app.vercel.app`
- [ ] **Registration Works**: Create a test account
- [ ] **Login Works**: Login with test account
- [ ] **Search Works**: Run a test search
- [ ] **Database Persists**: Logout/login, data still there
- [ ] **CORS Configured**: No CORS errors in browser console
- [ ] **Environment Variables**: Backend has all required vars
- [ ] **Migrations Ran**: Database tables exist
- [ ] **Logs Clean**: No errors in Railway/Vercel logs

---

## Monitoring & Logs

### Railway Logs

**Via CLI**:
```bash
# View live logs
railway logs

# Follow logs (like tail -f)
railway logs -f

# View last 100 lines
railway logs --lines 100
```

**Via Dashboard**:
1. Open project → Select service
2. Click **"Deployments"** tab
3. Select deployment
4. View **"Logs"** section

**What to Monitor**:
- ❌ Database connection errors
- ❌ Authentication failures
- ❌ API key errors
- ❌ Migration failures
- ✅ Successful API requests
- ✅ Search completions

### Vercel Logs

**Via CLI**:
```bash
# View deployment logs
vercel logs <deployment-url>

# Follow logs
vercel logs --follow
```

**Via Dashboard**:
1. Open project
2. Go to **"Deployments"** tab
3. Select deployment
4. View **"Build Logs"** and **"Function Logs"**

**What to Monitor**:
- ❌ Build failures
- ❌ Runtime errors
- ❌ API connection failures
- ✅ Successful page loads
- ✅ API requests

### Health Monitoring

Set up external monitoring (optional):

**Options**:
1. **UptimeRobot** (free) - [uptimerobot.com](https://uptimerobot.com/)
   - Monitor: `https://your-app.railway.app/api/health`
   - Check interval: 5 minutes
   - Alert via email/SMS

2. **Pingdom** - [pingdom.com](https://www.pingdom.com/)

3. **Better Uptime** - [betteruptime.com](https://betteruptime.com/)

---

## CI/CD Setup

### GitHub Actions (Automatic Deployment)

Both Railway and Vercel support automatic deployments from GitHub.

#### Railway Auto-Deploy

1. **Connect GitHub** (if not already):
   - Railway Dashboard → Project → Settings
   - Under **"Source"**, click **"Connect GitHub"**
   - Select repository
   - Select branch (e.g., `main`)

2. **Configure Deployment**:
   - Railway automatically deploys on push to selected branch
   - Runs migrations via [backend/start.sh](backend/start.sh)

#### Vercel Auto-Deploy

1. **Connect GitHub** (if not already):
   - Vercel Dashboard → Project → Settings
   - Under **"Git"**, click **"Connect Git Repository"**
   - Select repository

2. **Configure Deployment**:
   - Production: Deploys from `main` branch
   - Preview: Creates preview URLs for PRs

#### Custom GitHub Actions Workflow

Create [.github/workflows/deploy.yml](.github/workflows/deploy.yml):

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r backend/requirements.txt

    - name: Run tests
      run: |
        python test_imports.py
        # Add more tests here

  deploy-backend:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Railway
      run: |
        # Railway auto-deploys via webhook
        echo "Railway will auto-deploy backend"

  deploy-frontend:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Vercel
      run: |
        # Vercel auto-deploys via webhook
        echo "Vercel will auto-deploy frontend"
```

---

## Troubleshooting

### Backend Issues

#### Health Check Returns 502/503

**Causes**:
- Backend didn't start properly
- Migrations failed
- Database connection issue

**Solutions**:
```bash
# Check Railway logs
railway logs

# Look for errors like:
# - "Database connection failed"
# - "Migration error"
# - "Port already in use"

# Verify DATABASE_URL is set
railway variables | grep DATABASE_URL

# Trigger redeploy
railway up --detach
```

#### CORS Errors in Browser

**Error**: `Access to fetch at '...' has been blocked by CORS policy`

**Solution**:
```bash
# Check CORS_ORIGINS includes your frontend URL
railway variables | grep CORS_ORIGINS

# Update CORS_ORIGINS
railway variables set CORS_ORIGINS='["https://your-app.vercel.app"]'

# Verify format is correct JSON array with quotes
```

#### Database Migration Failures

**Error**: `ERROR [alembic.util.messaging] Can't locate revision`

**Solution**:
```bash
# Connect to Railway database
railway connect postgres

# Check alembic_version table
SELECT * FROM alembic_version;

# If corrupted, reset:
DELETE FROM alembic_version;

# Exit psql
\q

# Redeploy (migrations will run)
railway up --detach
```

#### Environment Variable Not Working

**Symptoms**: Backend logs show `None` for API keys

**Solution**:
```bash
# List all variables
railway variables

# Verify variable exists and has correct name
# Re-set if needed
railway variables set ANTHROPIC_API_KEY="sk-ant-xxx"

# Restart service
railway restart
```

### Frontend Issues

#### Build Fails on Vercel

**Error**: `Error: Command "npm run build" exited with 1`

**Solutions**:
1. Check **Build Logs** in Vercel Dashboard
2. Common issues:
   - Missing dependencies: Run `npm install` locally
   - TypeScript errors: Run `npm run build` locally
   - ESLint errors: Run `npm run lint` locally

```bash
# Test build locally
cd frontend
npm install
npm run build

# If it works locally but fails on Vercel:
# - Check Node.js version in Vercel settings
# - Ensure all dependencies in package.json
```

#### "Failed to Load" Errors

**Symptoms**: Frontend loads but can't connect to backend

**Solutions**:
1. Check `NEXT_PUBLIC_API_URL` in Vercel:
   ```bash
   # Should be your Railway backend URL
   NEXT_PUBLIC_API_URL=https://your-app.railway.app
   ```

2. Verify no trailing slash:
   ```bash
   # ❌ Wrong
   NEXT_PUBLIC_API_URL=https://your-app.railway.app/

   # ✅ Correct
   NEXT_PUBLIC_API_URL=https://your-app.railway.app
   ```

3. Check browser console (F12) for actual errors

#### Preview Deployment Not Working

**Issue**: Preview URLs don't have correct environment variables

**Solution**:
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Ensure `NEXT_PUBLIC_API_URL` is enabled for **"Preview"** environment
3. Redeploy the preview

### Database Issues

#### Connection Timeout

**Error**: `asyncpg.exceptions.ConnectionDoesNotExistError`

**Solutions**:
```bash
# Check DATABASE_URL is set
railway variables | grep DATABASE_URL

# Verify PostgreSQL plugin is running
railway status

# Restart database
railway restart
```

#### No Tables After Deployment

**Issue**: Backend runs but database is empty

**Solution**:
```bash
# Check if migrations ran in deployment logs
railway logs | grep "alembic"

# Look for: "Running database migrations..."
# and: "Running upgrade ... -> ..., <migration_name>"

# If migrations didn't run, check start.sh executed:
railway logs | grep "start.sh"

# Manually run migrations:
railway run alembic upgrade head
```

---

## Maintenance

### Regular Tasks

#### Weekly
- [ ] Check Railway/Vercel logs for errors
- [ ] Monitor API usage (Anthropic, Brave)
- [ ] Review failed searches/errors

#### Monthly
- [ ] Database backup (Railway auto-backs up, but export a copy)
- [ ] Update dependencies if needed
- [ ] Review and optimize database queries
- [ ] Clean up old test data

#### Quarterly
- [ ] Update Python/Node.js versions
- [ ] Update framework versions (FastAPI, Next.js)
- [ ] Security audit
- [ ] Performance review

### Updating the Application

#### Backend Updates

```bash
# 1. Update code locally
git pull origin main

# 2. Test locally
cd backend
source .venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload

# 3. Commit and push
git add .
git commit -m "Update backend"
git push origin main

# Railway auto-deploys
```

#### Frontend Updates

```bash
# 1. Update code locally
cd frontend
npm install

# 2. Test locally
npm run dev

# 3. Commit and push
git add .
git commit -m "Update frontend"
git push origin main

# Vercel auto-deploys
```

### Scaling

#### Railway Scaling

**Vertical Scaling** (more resources):
1. Railway Dashboard → Project → Service
2. Settings → Resources
3. Upgrade plan for more CPU/RAM

**Horizontal Scaling** (not available on free tier):
- Requires Railway Pro plan
- Multiple instances with load balancing

#### Vercel Scaling

- **Automatic** - Vercel automatically scales based on traffic
- **No configuration needed**
- **Free tier limits**: 100 GB bandwidth/month

---

## Cost Estimation

### Railway Costs

**Free Tier**:
- $5 credit per month
- Typical usage: $3-5/month
  - Backend: ~$2-3/month
  - PostgreSQL: ~$1-2/month

**After Free Credits**:
- Pay-as-you-go: ~$5-10/month for hobby projects
- Pro: $20/month for production apps

### Vercel Costs

**Free Tier (Hobby)**:
- Unlimited bandwidth (fair use)
- 100 GB-hours/month
- Perfect for hobby projects

**Pro Tier** ($20/month):
- Commercial use
- Better performance
- Team collaboration

### Total Monthly Cost

| Tier | Railway | Vercel | Total |
|------|---------|--------|-------|
| Free (hobby) | $0 ($5 credit) | $0 | $0-5 |
| Paid (hobby) | $5-10 | $0 | $5-10 |
| Production | $20-30 | $20 | $40-50 |

Plus API costs:
- Anthropic: ~$1-2 per search × searches/month
- Brave: Free (2,000 queries/month)

---

## Quick Reference

### Essential Commands

```bash
# Railway
railway login
railway init
railway add postgresql
railway variables set KEY="value"
railway up
railway logs
railway connect postgres
railway domain

# Vercel
vercel login
vercel
vercel --prod
vercel env add NEXT_PUBLIC_API_URL production
vercel logs
```

### URLs to Bookmark

- [Railway Dashboard](https://railway.app/dashboard)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Anthropic Console](https://console.anthropic.com/)
- [Brave API Dashboard](https://api.search.brave.com/app/dashboard)

---

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

---

**Deployment Complete!** 🚀

Your application is now live in production. For local development, see [README.md](README.md). For database management, see [DATABASE_SETUP.md](DATABASE_SETUP.md).
