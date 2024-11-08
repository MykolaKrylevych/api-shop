import os
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel
from logging.config import dictConfig
import logging
import stripe

load_dotenv(find_dotenv())


class Settings:
    BASE_URL: str = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    PAYMENT_WEBHOOK_URL: str = os.getenv("PAYMENT_WEBHOOK_URL", "http://127.0.0.1:8000/payment/webhook")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET")
    PROJECT_NAME: str = "BETA"
    PROJECT_VERSION: str = "1.0.0"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tdd")
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    STATIC_DIR: str = os.getenv("STATIC_DIR", "static/images")
    USERMANAGER_SECRET: str = os.getenv("USERMANAGER_SECRET")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY")


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "Candyshop"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "console": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
        },
        "file": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": False
        }
    }
    handlers: dict = {
        "console": {
            "formatter": "console",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": "app.log",

        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["console", "file"], "level": LOG_LEVEL},
    }


settings = Settings()

dictConfig(LogConfig().dict())

logger = logging.getLogger("Candyshop")

stripe.api_key = settings.STRIPE_SECRET_KEY
# FOR PRODUCTION
# stripe.WebhookEndpoint.create(
#     url=settings.PAYMENT_WEBHOOK_URL,
#     enabled_events=["checkout.session.completed", "checkout.session.async_payment_succeeded",
#                     "checkout.session.async_payment_failed"]
# )
