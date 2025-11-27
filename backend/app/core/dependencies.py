"""Dependency injection for services."""
from app.services.vector_db import vector_db, VectorDBService
from app.services.email import email_service, EmailService
from app.services.scraper import WebScraper


def get_vector_db_service() -> VectorDBService:
    """Get vector database service instance."""
    return vector_db


def get_email_service() -> EmailService:
    """Get email service instance."""
    return email_service


def get_scraper_service() -> WebScraper:
    """Get web scraper service instance."""
    return WebScraper()
