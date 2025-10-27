from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
sys.path.append('/app')

from . import models, database
from .routers import analytics
from .event_processor import EventProcessor
from shared.rabbitmq_client import setup_rabbitmq_infrastructure

event_processor = EventProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("Starting Analytics Service...")

    # Create database tables
    models.Base.metadata.create_all(bind=database.engine)

    # Setup RabbitMQ infrastructure
    try:
        setup_rabbitmq_infrastructure()
    except Exception as e:
        print(f"Failed to setup RabbitMQ infrastructure: {e}")

    # Start event consumers in background threads
    try:
        event_processor.start_all_consumers()
        print("Event consumers started successfully")
    except Exception as e:
        print(f"Failed to start event consumers: {e}")

    yield

    # Shutdown
    print("Shutting down Analytics Service...")

app = FastAPI(
    title="Analytics Service",
    description="Microservice for analytics and statistics",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"service": "Analytics Service", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Include routers
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
