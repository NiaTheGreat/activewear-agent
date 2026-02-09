import logging
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import activities, auth, manufacturers, organizations, pipelines, presets, search
from app.config import settings

# Configure logging with Central Time timestamps
CT = timezone(timedelta(hours=-6))


class CentralTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct_time = datetime.fromtimestamp(record.created, tz=CT)
        if datefmt:
            return ct_time.strftime(datefmt)
        return ct_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


formatter = CentralTimeFormatter(
    fmt="%(asctime)s CT | %(levelname)s | %(name)s | %(message)s"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])
logging.getLogger("app").setLevel(logging.DEBUG)

_is_prod = settings.ENVIRONMENT == "production"

app = FastAPI(
    title="Manufacturer Research Agent API",
    version="1.0.0",
    description="API backend for the activewear manufacturer research agent",
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
)

# CORS - log the origins for debugging
logging.info(f"CORS_ORIGINS configured: {settings.CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(pipelines.router)
app.include_router(presets.router)
app.include_router(search.router)
app.include_router(manufacturers.router)
app.include_router(activities.router)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
