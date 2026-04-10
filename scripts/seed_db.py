"""Seed database with sample data"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    """Seed the database with sample data"""
    logger.info("🌱 Seeding database with sample data...")

    # TODO: Add sample data creation
    # - Sample pipelines
    # - Sample models
    # - Sample runs

    logger.info("✅ Database seeding complete!")


if __name__ == "__main__":
    seed_database()
