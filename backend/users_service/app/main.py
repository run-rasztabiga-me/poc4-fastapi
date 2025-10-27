from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
sys.path.append('/app')

from . import models, database
from .routers import users
from shared.rabbitmq_client import setup_rabbitmq_infrastructure

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("Starting Users Service...")

    # Create database tables
    models.Base.metadata.create_all(bind=database.engine)

    # Setup RabbitMQ infrastructure
    try:
        setup_rabbitmq_infrastructure()
    except Exception as e:
        print(f"Failed to setup RabbitMQ infrastructure: {e}")

    yield

    # Shutdown
    print("Shutting down Users Service...")

app = FastAPI(
    title="Users Service",
    description="Microservice for user management and authentication",
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
    return {"service": "Users Service", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
