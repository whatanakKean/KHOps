"""Base Service with CRUD operations"""

from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service with common CRUD operations"""
    
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new object"""
        try:
            db_obj = self.model(**obj_in.model_dump())
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    async def get(self, obj_id: int) -> Optional[ModelType]:
        """Get object by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == obj_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__}: {str(e)}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 10, filters: Optional[dict] = None) -> List[ModelType]:
        """Get all objects with pagination"""
        try:
            query = self.db.query(self.model)
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} list: {str(e)}")
            raise
    
    async def get_count(self, filters: Optional[dict] = None) -> int:
        """Get total count of objects"""
        try:
            query = self.db.query(self.model)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise
    
    async def update(self, obj_id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update an object"""
        try:
            db_obj = await self.get(obj_id)
            if not db_obj:
                return None
            
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} {obj_id}")
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise
    
    async def delete(self, obj_id: int) -> bool:
        """Delete an object"""
        try:
            db_obj = await self.get(obj_id)
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            logger.info(f"Deleted {self.model.__name__} {obj_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {str(e)}")
            raise
