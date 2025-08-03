from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import pandas as pd
import os
import shutil
from typing import List
from datetime import datetime

from app.models.database import get_db
from app.models.user import User
from app.models.dataset import Dataset, DatasetResponse
from app.utils.auth import get_current_active_user
from app.utils.data_processing import (
    validate_csv_file,
    save_dataframe_info,
    get_dataframe_preview
)

router = APIRouter()

@router.post("/csv", response_model=DatasetResponse)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a CSV file and create a dataset."""
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Check file size (10MB limit)
    max_size = int(os.getenv("MAX_FILE_SIZE", 10485760))
    if file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {max_size / 1024 / 1024}MB limit"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.id}_{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate CSV file
        is_valid, message = validate_csv_file(file_path)
        if not is_valid:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Read and process the CSV
        df = pd.read_csv(file_path)
        
        # Get dataset metadata
        metadata = save_dataframe_info(df, file_path, current_user.id)
        
        # Create dataset record
        dataset = Dataset(
            name=file.filename.replace('.csv', ''),
            filename=filename,
            file_path=file_path,
            file_size=metadata['file_size'],
            row_count=metadata['row_count'],
            column_count=metadata['column_count'],
            column_info=metadata['column_info'],
            user_id=current_user.id
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        return dataset
        
    except Exception as e:
        # Clean up file if error occurs
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/datasets", response_model=List[DatasetResponse])
async def get_datasets(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all datasets for the current user."""
    datasets = db.query(Dataset).filter(Dataset.user_id == current_user.id).all()
    return datasets

@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific dataset by ID."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return dataset

@router.get("/datasets/{dataset_id}/preview")
async def get_dataset_preview(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a preview of the dataset."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    try:
        df = pd.read_csv(dataset.file_path)
        preview = get_dataframe_preview(df)
        return preview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading dataset: {str(e)}"
        )

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a dataset."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Delete the file
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    
    # Delete from database
    db.delete(dataset)
    db.commit()
    
    return {"message": "Dataset deleted successfully"} 