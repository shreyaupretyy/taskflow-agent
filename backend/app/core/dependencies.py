"""Dependency injection for services."""

from app.services.email import EmailService, email_service
from app.services.scraper import WebScraper
from app.services.vector_db import VectorDBService, vector_db


def get_vector_db_service() -> VectorDBService:
    """Get vector database service instance."""
    return vector_db


def get_email_service() -> EmailService:
    """Get email service instance."""
    return email_service


def get_scraper_service() -> WebScraper:
    """Get web scraper service instance."""
    return WebScraper()
