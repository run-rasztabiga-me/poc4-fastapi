import os

class Config:
    """Shared configuration for all microservices"""

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

    # RabbitMQ
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://rabbitmq:rabbitmq@localhost:5672/")

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))

    # Services URLs
    USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8002")
    NOTES_SERVICE_URL = os.getenv("NOTES_SERVICE_URL", "http://localhost:8001")
    ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8003")

config = Config()
