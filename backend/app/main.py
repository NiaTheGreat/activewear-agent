from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, manufacturers, presets, search
from app.config import settings

app = FastAPI(
    title="Manufacturer Research Agent API",
    version="1.0.0",
    description="API backend for the activewear manufacturer research agent",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(presets.router)
app.include_router(search.router)
app.include_router(manufacturers.router)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
