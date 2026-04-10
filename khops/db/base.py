"""SQLAlchemy Base Configuration"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

# SQLAlchemy declarative base for models
Base = declarative_base()

# Metadata object for explicit table reflection if needed
metadata = MetaData()
