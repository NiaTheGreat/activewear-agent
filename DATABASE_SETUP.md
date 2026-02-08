# Database Setup Guide

Complete guide for setting up PostgreSQL for the Activewear Agent application, both locally and in production.

---

## Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Manual PostgreSQL Installation](#manual-postgresql-installation)
3. [Database Configuration](#database-configuration)
4. [Running Migrations](#running-migrations)
5. [Connecting to the Database](#connecting-to-the-database)
6. [Database Schema Overview](#database-schema-overview)
7. [Production Setup (Railway)](#production-setup-railway)
8. [Backup and Restore](#backup-and-restore)
9. [Common Operations](#common-operations)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start (Docker)

**Recommended for local development** - Fastest and most consistent setup.

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Steps

1. **Start PostgreSQL**

```bash
# From project root
docker-compose up -d

# Verify it's running
docker ps
```

You should see output like:
```
CONTAINER ID   IMAGE                  STATUS         PORTS
abc123def456   postgres:15-alpine     Up 10 seconds  0.0.0.0:5432->5432/tcp
```

2. **Verify Database Created**

```bash
docker exec -it manufacturer-agent-db psql -U agent_user -d manufacturer_agent -c "\dt"
```

If the database is empty (no tables), that's expected - migrations will create them.

3. **Run Migrations** (creates tables)

```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
alembic upgrade head
```

4. **Verify Tables Created**

```bash
docker exec -it manufacturer-agent-db psql -U agent_user -d manufacturer_agent -c "\dt"
```

You should see:
```
            List of relations
 Schema |      Name       | Type  |   Owner
--------+-----------------+-------+------------
 public | manufacturers   | table | agent_user
 public | presets        | table | agent_user
 public | searches       | table | agent_user
 public | users          | table | agent_user
```

### Docker Compose Configuration

The [docker-compose.yml](docker-compose.yml) file configures:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: manufacturer-agent-db
    environment:
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: agent_password
      POSTGRES_DB: manufacturer_agent
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

**Default Credentials**:
- **Database**: `manufacturer_agent`
- **Username**: `agent_user`
- **Password**: `agent_password`
- **Host**: `localhost`
- **Port**: `5432`

### Stopping and Starting

```bash
# Stop PostgreSQL (keeps data)
docker-compose stop

# Start PostgreSQL again
docker-compose start

# Stop and remove container (keeps data volume)
docker-compose down

# Stop and remove ALL data (⚠️ destructive)
docker-compose down -v
```

---

## Manual PostgreSQL Installation

If you prefer not to use Docker or need a system-wide PostgreSQL installation.

### macOS

#### Option 1: Homebrew (Recommended)

```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Verify it's running
psql --version
```

#### Option 2: Postgres.app

1. Download from [Postgres.app](https://postgresapp.com/)
2. Drag to Applications folder
3. Open Postgres.app
4. PostgreSQL will start automatically

### Linux (Ubuntu/Debian)

```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

# Import repository signing key
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Update package list
sudo apt-get update

# Install PostgreSQL 15
sudo apt-get install -y postgresql-15

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

### Windows

1. Download installer from [PostgreSQL.org](https://www.postgresql.org/download/windows/)
2. Run the installer
3. Follow the setup wizard:
   - Choose installation directory
   - Select components (PostgreSQL Server, pgAdmin, Command Line Tools)
   - Set password for `postgres` user
   - Use default port `5432`
   - Complete installation

4. Add PostgreSQL to PATH (if not done automatically):
   - Search for "Environment Variables"
   - Edit PATH variable
   - Add: `C:\Program Files\PostgreSQL\15\bin`

### Create Database and User

After installing PostgreSQL, create the application database:

```bash
# Connect as postgres superuser
psql -U postgres

# In psql:
CREATE DATABASE manufacturer_agent;
CREATE USER agent_user WITH PASSWORD 'agent_password';
GRANT ALL PRIVILEGES ON DATABASE manufacturer_agent TO agent_user;

# Grant schema privileges (PostgreSQL 15+)
\c manufacturer_agent
GRANT ALL ON SCHEMA public TO agent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agent_user;

# Exit psql
\q
```

**Security Note**: For production, use a strong password and store it securely:
```bash
# Generate strong password
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Database Configuration

### Backend Configuration

Edit [backend/.env](backend/.env):

```bash
# For Docker setup
DATABASE_URL=postgresql+asyncpg://agent_user:agent_password@localhost:5432/manufacturer_agent

# For manual PostgreSQL (same format)
DATABASE_URL=postgresql+asyncpg://agent_user:agent_password@localhost:5432/manufacturer_agent
```

**Important**:
- Use `postgresql+asyncpg://` (not `postgresql://`) for async SQLAlchemy
- For synchronous operations (like Alembic migrations), use `postgresql://` or set `DATABASE_URL_SYNC`

### Database URL Format

```
postgresql+asyncpg://username:password@host:port/database_name
```

**Components**:
- `postgresql+asyncpg://` - Async driver
- `username` - Database user (default: `agent_user`)
- `password` - User's password (default: `agent_password`)
- `host` - Server hostname (default: `localhost`)
- `port` - PostgreSQL port (default: `5432`)
- `database_name` - Database name (default: `manufacturer_agent`)

### Connection Pooling

The backend uses SQLAlchemy's async connection pool. Configuration in [backend/app/database.py](backend/app/database.py):

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=5,
    max_overflow=10,
)
```

---

## Running Migrations

Alembic manages database schema migrations.

### Initial Setup

```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Check current migration status
alembic current

# View migration history
alembic history

# Apply all migrations
alembic upgrade head
```

### Common Migration Commands

```bash
# Apply migrations up to a specific version
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback to a specific version
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base

# Show current version
alembic current

# Show migration history
alembic history --verbose
```

### Creating New Migrations

When you modify database models in [backend/app/models/](backend/app/models/):

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to users"

# Review the generated migration file in:
# backend/alembic/versions/xxxxx_add_new_column_to_users.py

# Edit if needed, then apply:
alembic upgrade head
```

### Migration Files Location

- **Configuration**: [backend/alembic.ini](backend/alembic.ini)
- **Migration Scripts**: [backend/alembic/versions/](backend/alembic/versions/)
- **Alembic Environment**: [backend/alembic/env.py](backend/alembic/env.py)

---

## Connecting to the Database

### Method 1: psql (PostgreSQL CLI)

```bash
# Connect to database
psql -h localhost -U agent_user -d manufacturer_agent

# When prompted, enter password: agent_password
```

**Common psql commands**:
```sql
-- List all tables
\dt

-- Describe table structure
\d users
\d searches
\d manufacturers
\d presets

-- List all databases
\l

-- Show current connection info
\conninfo

-- Execute SQL
SELECT * FROM users;
SELECT COUNT(*) FROM searches;

-- Quit
\q
```

### Method 2: DBeaver (GUI - Recommended)

1. Download [DBeaver](https://dbeaver.io/download/)
2. Open DBeaver
3. Click "New Database Connection"
4. Select "PostgreSQL"
5. Enter connection details:
   - **Host**: `localhost`
   - **Port**: `5432`
   - **Database**: `manufacturer_agent`
   - **Username**: `agent_user`
   - **Password**: `agent_password`
6. Click "Test Connection"
7. Click "Finish"

**Features**:
- Visual query builder
- Schema browser
- Data editor
- SQL autocomplete
- Export to CSV/JSON/Excel

### Method 3: pgAdmin (GUI)

1. Download [pgAdmin](https://www.pgadmin.org/download/)
2. Open pgAdmin
3. Right-click "Servers" → "Create" → "Server"
4. **General tab**:
   - Name: `Manufacturer Agent Local`
5. **Connection tab**:
   - Host: `localhost`
   - Port: `5432`
   - Database: `manufacturer_agent`
   - Username: `agent_user`
   - Password: `agent_password`
   - Save password: ✓
6. Click "Save"

### Method 4: TablePlus (GUI - macOS/Windows)

1. Download [TablePlus](https://tableplus.com/)
2. Create new connection
3. Select PostgreSQL
4. Enter details:
   - **Host**: `localhost`
   - **Port**: `5432`
   - **User**: `agent_user`
   - **Password**: `agent_password`
   - **Database**: `manufacturer_agent`
5. Test and connect

### Method 5: Python Script

```python
import asyncio
import asyncpg

async def test_connection():
    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='agent_user',
        password='agent_password',
        database='manufacturer_agent'
    )

    # Query users
    rows = await conn.fetch('SELECT * FROM users')
    for row in rows:
        print(f"User: {row['email']}")

    # Query searches
    count = await conn.fetchval('SELECT COUNT(*) FROM searches')
    print(f"Total searches: {count}")

    # Close connection
    await conn.close()

# Run
asyncio.run(test_connection())
```

### Method 6: From Backend Code

```python
# In backend Python code
from app.database import get_db

async def example():
    async for db in get_db():
        result = await db.execute(
            "SELECT * FROM users WHERE email = :email",
            {"email": "user@example.com"}
        )
        user = result.fetchone()
        print(user)
```

---

## Database Schema Overview

### Tables

#### 1. `users` - User accounts
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. `searches` - Search history
```sql
CREATE TABLE searches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    criteria JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    progress INTEGER DEFAULT 0,
    max_manufacturers INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

#### 3. `manufacturers` - Manufacturer results
```sql
CREATE TABLE manufacturers (
    id SERIAL PRIMARY KEY,
    search_id INTEGER REFERENCES searches(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    website VARCHAR(500),
    moq VARCHAR(255),
    moq_description TEXT,
    match_score DECIMAL(5,2),
    confidence VARCHAR(20),
    materials TEXT[],
    certifications TEXT[],
    production_methods TEXT[],
    email VARCHAR(255),
    phone VARCHAR(100),
    address TEXT,
    notes TEXT,
    website_signals JSONB,
    source_url VARCHAR(500),
    is_favorite BOOLEAN DEFAULT FALSE,
    user_notes TEXT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. `presets` - Saved search criteria
```sql
CREATE TABLE presets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    criteria JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Relationships

```
users (1) ──→ (many) searches
searches (1) ──→ (many) manufacturers
users (1) ──→ (many) presets
```

### Indexes

```sql
-- Email lookup (authentication)
CREATE INDEX idx_users_email ON users(email);

-- User's searches
CREATE INDEX idx_searches_user_id ON searches(user_id);

-- Search's manufacturers
CREATE INDEX idx_manufacturers_search_id ON manufacturers(search_id);

-- Favorite manufacturers
CREATE INDEX idx_manufacturers_favorite ON manufacturers(is_favorite);

-- User's presets
CREATE INDEX idx_presets_user_id ON presets(user_id);
```

### View Schema in psql

```bash
psql -h localhost -U agent_user -d manufacturer_agent

# Table structure
\d users
\d searches
\d manufacturers
\d presets

# All tables
\dt

# All indexes
\di
```

---

## Production Setup (Railway)

### Automated Setup (Recommended)

Railway automatically provisions PostgreSQL when you add the plugin:

```bash
# Login to Railway
railway login

# Link to your project
railway link

# Add PostgreSQL plugin (via Railway dashboard or CLI)
railway add postgresql

# Railway automatically sets DATABASE_URL environment variable
# No additional configuration needed!
```

### Manual Connection

Get the connection details:

```bash
# View all environment variables (including DATABASE_URL)
railway variables

# Or via Railway dashboard:
# Project → PostgreSQL service → Connect tab
```

The `DATABASE_URL` format:
```
postgresql://user:password@host:port/database
```

### Connecting to Production Database

#### Option 1: Railway CLI

```bash
# Connect via Railway CLI
railway connect postgres

# This opens a psql session to your production database
```

#### Option 2: Direct Connection

```bash
# Get DATABASE_URL from Railway
railway variables | grep DATABASE_URL

# Connect using psql
psql "postgresql://user:password@host.railway.app:port/database"
```

#### Option 3: GUI Tool (DBeaver/pgAdmin)

1. Get connection details from Railway dashboard
2. Create new connection in your GUI tool:
   - **Host**: `containers-us-west-xxx.railway.app` (from Railway)
   - **Port**: `5432`
   - **Database**: `railway`
   - **Username**: `postgres`
   - **Password**: (from Railway dashboard)
   - **SSL Mode**: `require`

### Running Migrations in Production

Railway runs migrations automatically on deployment via [backend/start.sh](backend/start.sh):

```bash
#!/bin/bash
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
```

To run migrations manually:

```bash
# Connect to Railway
railway link

# Run migrations
railway run alembic upgrade head
```

### Production Database Backup

```bash
# Backup production database
railway run pg_dump > backup_$(date +%Y%m%d).sql

# Or via direct connection
pg_dump "postgresql://user:pass@host:port/db" > backup.sql
```

---

## Backup and Restore

### Local Backup

#### Full Database Backup

```bash
# Backup entire database
pg_dump -h localhost -U agent_user manufacturer_agent > backup_$(date +%Y%m%d).sql

# Backup with compression
pg_dump -h localhost -U agent_user manufacturer_agent | gzip > backup_$(date +%Y%m%d).sql.gz
```

#### Specific Table Backup

```bash
# Backup single table
pg_dump -h localhost -U agent_user -t users manufacturer_agent > users_backup.sql

# Backup multiple tables
pg_dump -h localhost -U agent_user -t users -t searches manufacturer_agent > backup.sql
```

#### Data-Only Backup (No Schema)

```bash
pg_dump -h localhost -U agent_user --data-only manufacturer_agent > data_backup.sql
```

#### Schema-Only Backup (No Data)

```bash
pg_dump -h localhost -U agent_user --schema-only manufacturer_agent > schema_backup.sql
```

### Local Restore

#### Full Database Restore

```bash
# Drop and recreate database
dropdb -h localhost -U agent_user manufacturer_agent
createdb -h localhost -U agent_user manufacturer_agent

# Restore from backup
psql -h localhost -U agent_user manufacturer_agent < backup_20260208.sql
```

#### Restore Without Dropping

```bash
# Restore into existing database
psql -h localhost -U agent_user manufacturer_agent < backup.sql
```

#### Restore Compressed Backup

```bash
gunzip < backup_20260208.sql.gz | psql -h localhost -U agent_user manufacturer_agent
```

### Production Backup (Railway)

```bash
# Backup production to local file
railway run pg_dump > production_backup_$(date +%Y%m%d).sql

# Or via direct connection
pg_dump "$(railway variables | grep DATABASE_URL | cut -d'=' -f2-)" > backup.sql
```

### Automated Backups

Create a backup script [scripts/backup.sh](scripts/backup.sh):

```bash
#!/bin/bash
BACKUP_DIR="$HOME/backups/manufacturer-agent"
mkdir -p "$BACKUP_DIR"

# Local backup
pg_dump -h localhost -U agent_user manufacturer_agent | \
  gzip > "$BACKUP_DIR/local_$(date +%Y%m%d_%H%M%S).sql.gz"

echo "Backup complete: $BACKUP_DIR"

# Keep only last 7 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
```

Set up cron job (macOS/Linux):
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/scripts/backup.sh
```

---

## Common Operations

### User Management

```sql
-- Create new user
INSERT INTO users (email, hashed_password)
VALUES ('user@example.com', '$hashed_password');

-- Find user by email
SELECT * FROM users WHERE email = 'user@example.com';

-- Delete user (cascades to searches, presets)
DELETE FROM users WHERE email = 'user@example.com';

-- Count users
SELECT COUNT(*) FROM users;
```

### Search Management

```sql
-- View recent searches
SELECT id, user_id, status, created_at
FROM searches
ORDER BY created_at DESC
LIMIT 10;

-- Find searches by status
SELECT * FROM searches WHERE status = 'completed';

-- Search with user info
SELECT s.id, u.email, s.status, s.created_at
FROM searches s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC;

-- Delete old searches (older than 30 days)
DELETE FROM searches
WHERE created_at < NOW() - INTERVAL '30 days';
```

### Manufacturer Management

```sql
-- Top manufacturers by score
SELECT name, location, match_score
FROM manufacturers
WHERE search_id = 1
ORDER BY match_score DESC
LIMIT 10;

-- Favorite manufacturers
SELECT name, location, website
FROM manufacturers
WHERE is_favorite = true;

-- Manufacturers with specific certification
SELECT name, certifications
FROM manufacturers
WHERE 'OEKO-TEX' = ANY(certifications);

-- Average match score per search
SELECT search_id, AVG(match_score) as avg_score
FROM manufacturers
GROUP BY search_id;
```

### Data Cleanup

```sql
-- Delete searches with no manufacturers
DELETE FROM searches
WHERE id NOT IN (SELECT DISTINCT search_id FROM manufacturers);

-- Remove duplicate manufacturers (by website)
DELETE FROM manufacturers m1
USING manufacturers m2
WHERE m1.id < m2.id
  AND m1.website = m2.website
  AND m1.search_id = m2.search_id;
```

### Statistics

```sql
-- Database statistics
SELECT
  (SELECT COUNT(*) FROM users) as total_users,
  (SELECT COUNT(*) FROM searches) as total_searches,
  (SELECT COUNT(*) FROM manufacturers) as total_manufacturers,
  (SELECT COUNT(*) FROM presets) as total_presets;

-- Searches per user
SELECT u.email, COUNT(s.id) as search_count
FROM users u
LEFT JOIN searches s ON u.id = s.user_id
GROUP BY u.email
ORDER BY search_count DESC;

-- Average manufacturers per search
SELECT AVG(manufacturer_count) as avg_manufacturers
FROM (
  SELECT search_id, COUNT(*) as manufacturer_count
  FROM manufacturers
  GROUP BY search_id
) subquery;
```

---

## Troubleshooting

### Connection Refused

**Error**: `psql: error: connection to server at "localhost" (::1), port 5432 failed: Connection refused`

**Solutions**:
```bash
# Check if PostgreSQL is running
# Docker:
docker ps | grep postgres

# macOS (Homebrew):
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql

# Start if not running
docker-compose up -d  # Docker
brew services start postgresql@15  # macOS
sudo systemctl start postgresql  # Linux
```

### Authentication Failed

**Error**: `psql: error: FATAL: password authentication failed for user "agent_user"`

**Solutions**:
1. Check credentials in [backend/.env](backend/.env)
2. Verify user exists:
   ```bash
   psql -U postgres -c "\du"
   ```
3. Recreate user:
   ```sql
   DROP USER IF EXISTS agent_user;
   CREATE USER agent_user WITH PASSWORD 'agent_password';
   GRANT ALL PRIVILEGES ON DATABASE manufacturer_agent TO agent_user;
   ```

### Database Does Not Exist

**Error**: `psql: error: FATAL: database "manufacturer_agent" does not exist`

**Solutions**:
```bash
# Create database
psql -U postgres -c "CREATE DATABASE manufacturer_agent;"

# Or use createdb
createdb -U postgres manufacturer_agent

# For Docker
docker exec -it manufacturer-agent-db createdb -U agent_user manufacturer_agent
```

### Port Already in Use

**Error**: `Error: bind: address already in use`

**Solutions**:
```bash
# Find process using port 5432
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux

# Or change PostgreSQL port in docker-compose.yml
ports:
  - "5433:5432"  # Use port 5433 instead

# Update DATABASE_URL
postgresql+asyncpg://agent_user:agent_password@localhost:5433/manufacturer_agent
```

### Migration Errors

**Error**: `sqlalchemy.exc.ProgrammingError: relation "users" does not exist`

**Solution**: Run migrations
```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

**Error**: `ERROR [alembic.util.messaging] Target database is not up to date`

**Solution**:
```bash
# Check current version
alembic current

# Apply missing migrations
alembic upgrade head
```

**Error**: `Can't locate revision identified by 'xxxxx'`

**Solution**: Reset alembic version
```sql
-- Connect to database
psql -h localhost -U agent_user -d manufacturer_agent

-- Check current version
SELECT * FROM alembic_version;

-- Delete version (if corrupted)
DELETE FROM alembic_version;

-- Exit and rerun migrations
\q

alembic upgrade head
```

### Permission Denied

**Error**: `permission denied for schema public`

**Solution**: Grant permissions
```sql
psql -U postgres -d manufacturer_agent

GRANT ALL ON SCHEMA public TO agent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agent_user;
```

### Docker Volume Issues

**Error**: Database resets after restart

**Solution**: Check volumes
```bash
# List volumes
docker volume ls

# Verify postgres_data volume exists
docker volume inspect activewear-agent_postgres_data

# If missing, recreate with:
docker-compose down
docker-compose up -d
```

### Connection Pool Exhausted

**Error**: `sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached`

**Solution**: Increase pool size in [backend/app/database.py](backend/app/database.py):
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,  # Increase from 5
    max_overflow=20,  # Increase from 10
)
```

---

## Best Practices

### Security

1. **Strong Passwords**: Use generated passwords in production
2. **Environment Variables**: Never commit `.env` files
3. **SSL**: Use SSL for production connections
4. **Least Privilege**: Grant only necessary permissions
5. **Regular Backups**: Automate daily backups

### Performance

1. **Indexes**: Add indexes on frequently queried columns
2. **Connection Pooling**: Use appropriate pool sizes
3. **Query Optimization**: Use EXPLAIN ANALYZE for slow queries
4. **Pagination**: Limit large result sets

### Maintenance

1. **Regular Backups**: Daily automated backups
2. **Monitor Disk Space**: Check database size regularly
3. **Vacuum**: Run VACUUM periodically (auto-vacuum enabled by default)
4. **Update PostgreSQL**: Keep PostgreSQL version current

---

## Quick Reference

### Essential Commands

```bash
# Start database (Docker)
docker-compose up -d

# Connect with psql
psql -h localhost -U agent_user -d manufacturer_agent

# Run migrations
cd backend && alembic upgrade head

# Backup database
pg_dump -h localhost -U agent_user manufacturer_agent > backup.sql

# Restore database
psql -h localhost -U agent_user manufacturer_agent < backup.sql

# Stop database (Docker)
docker-compose down
```

### Connection Strings

```bash
# Local (async)
postgresql+asyncpg://agent_user:agent_password@localhost:5432/manufacturer_agent

# Local (sync - for Alembic)
postgresql://agent_user:agent_password@localhost:5432/manufacturer_agent

# Production (Railway - auto-injected)
$DATABASE_URL
```

---

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Railway PostgreSQL Guide](https://docs.railway.app/databases/postgresql)

---

**Database Setup Complete!** 🎉

For web app setup, see [README.md](README.md). For deployment, see [README.md - Deployment](README.md#deployment).
