from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    row_count = Column(Integer)
    column_count = Column(Integer)
    column_info = Column(JSON)  # Store column types, missing values, etc.
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="datasets")
    models = relationship("Model", back_populates="dataset")

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    task_type = Column(String)  # classification, regression, clustering
    algorithm = Column(String)
    target_column = Column(String)
    feature_columns = Column(JSON)
    model_path = Column(String)
    metrics = Column(JSON)  # Store performance metrics
    parameters = Column(JSON)  # Store model parameters
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dataset = relationship("Dataset", back_populates="models")
    user = relationship("User", back_populates="models")

class DatasetCreate(BaseModel):
    name: str
    filename: str
    file_path: str
    file_size: int
    row_count: int
    column_count: int
    column_info: Dict[str, Any]

class DatasetResponse(BaseModel):
    id: int
    name: str
    filename: str
    file_size: int
    row_count: int
    column_count: int
    column_info: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class ModelCreate(BaseModel):
    name: str
    task_type: str
    algorithm: str
    target_column: str
    feature_columns: list
    model_path: str
    metrics: Dict[str, Any]
    parameters: Dict[str, Any]

class ModelResponse(BaseModel):
    id: int
    name: str
    task_type: str
    algorithm: str
    target_column: str
    feature_columns: list
    metrics: Dict[str, Any]
    parameters: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True 