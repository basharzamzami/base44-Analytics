from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_tables
from app.api import auth, tenants, connectors, kpis, alerts, ask, dashboard, predictions, graph

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Base44 - Palantir-for-SMBs Platform"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(connectors.router)
app.include_router(kpis.router)
app.include_router(alerts.router)
app.include_router(ask.router)
app.include_router(dashboard.router)
app.include_router(predictions.router)
app.include_router(graph.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Base44 API is running",
        "version": settings.version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": settings.version,
        "database": "connected",
        "timestamp": "2024-01-15T10:30:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

