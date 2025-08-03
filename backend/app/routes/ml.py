from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd
from typing import Dict, Any, List
from pydantic import BaseModel
import os

from app.models.database import get_db
from app.models.user import User
from app.models.dataset import Dataset, Model, ModelResponse
from app.utils.auth import get_current_active_user
from app.services.ml_service import MLService
from app.services.llm_service import LLMService

router = APIRouter()
ml_service = MLService()
llm_service = LLMService()

class ModelTrainingRequest(BaseModel):
    dataset_id: int
    task_type: str  # classification, regression, clustering
    target_column: str = None
    algorithm: str = "auto"
    n_clusters: int = 3

class ModelTrainingResponse(BaseModel):
    model_id: int
    task_type: str
    algorithm: str
    target_column: str = None
    feature_columns: List[str]
    metrics: Dict[str, Any]
    insights: str
    model_path: str

@router.post("/train", response_model=ModelTrainingResponse)
async def train_model(
    request: ModelTrainingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Train a machine learning model on a dataset."""
    
    # Get the dataset
    dataset = db.query(Dataset).filter(
        Dataset.id == request.dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    try:
        # Load the dataset
        df = pd.read_csv(dataset.file_path)
        
        # Train model based on task type
        if request.task_type == "classification":
            if not request.target_column:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Target column is required for classification"
                )
            
            model_data = ml_service.train_classification_model(
                df, request.target_column, request.algorithm
            )
            
        elif request.task_type == "regression":
            if not request.target_column:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Target column is required for regression"
                )
            
            model_data = ml_service.train_regression_model(
                df, request.target_column, request.algorithm
            )
            
        elif request.task_type == "clustering":
            model_data = ml_service.train_clustering_model(
                df, request.n_clusters
            )
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid task type. Must be classification, regression, or clustering"
            )
        
        # Save the model
        model_name = f"{dataset.name}_{request.task_type}_{request.algorithm}"
        model_path = ml_service.save_model(model_data, model_name)
        
        # Generate insights using LLM
        dataset_info = {
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "column_info": dataset.column_info
        }
        
        model_results = {
            "task_type": model_data["task_type"],
            "algorithm": model_data["algorithm"],
            "target_column": request.target_column,
            "feature_columns": model_data["feature_columns"],
            "metrics": model_data["metrics"]
        }
        
        insights = llm_service.generate_insights(dataset_info, model_results)
        
        # Save model record to database
        model_record = Model(
            name=model_name,
            task_type=model_data["task_type"],
            algorithm=model_data["algorithm"],
            target_column=request.target_column,
            feature_columns=model_data["feature_columns"],
            model_path=model_path,
            metrics=model_data["metrics"],
            parameters={"algorithm": request.algorithm, "n_clusters": request.n_clusters},
            dataset_id=dataset.id,
            user_id=current_user.id
        )
        
        db.add(model_record)
        db.commit()
        db.refresh(model_record)
        
        return ModelTrainingResponse(
            model_id=model_record.id,
            task_type=model_data["task_type"],
            algorithm=model_data["algorithm"],
            target_column=request.target_column,
            feature_columns=model_data["feature_columns"],
            metrics=model_data["metrics"],
            insights=insights,
            model_path=model_path
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error training model: {str(e)}"
        )

@router.get("/models", response_model=List[ModelResponse])
async def get_models(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all models for the current user."""
    models = db.query(Model).filter(Model.user_id == current_user.id).all()
    return models

@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific model by ID."""
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return model

@router.get("/models/{model_id}/results")
async def get_model_results(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed model results and insights."""
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    try:
        # Load the model data
        model_data = ml_service.load_model(model.model_path)
        
        # Get dataset info
        dataset = db.query(Dataset).filter(Dataset.id == model.dataset_id).first()
        
        # Generate insights
        dataset_info = {
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "column_info": dataset.column_info
        }
        
        model_results = {
            "task_type": model.task_type,
            "algorithm": model.algorithm,
            "target_column": model.target_column,
            "feature_columns": model.feature_columns,
            "metrics": model.metrics
        }
        
        insights = llm_service.generate_insights(dataset_info, model_results)
        
        return {
            "model": model,
            "metrics": model.metrics,
            "insights": insights,
            "model_data": {
                "algorithm": model_data["algorithm"],
                "task_type": model_data["task_type"],
                "feature_columns": model_data["feature_columns"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading model results: {str(e)}"
        )

@router.delete("/models/{model_id}")
async def delete_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a model."""
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Delete the model file
    if os.path.exists(model.model_path):
        os.remove(model.model_path)
    
    # Delete from database
    db.delete(model)
    db.commit()
    
    return {"message": "Model deleted successfully"}

@router.post("/models/{model_id}/predict")
async def make_prediction(
    model_id: int,
    data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Make predictions using a trained model."""
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    try:
        # Load the model
        model_data = ml_service.load_model(model.model_path)
        
        # Convert input data to DataFrame
        input_df = pd.DataFrame([data])
        
        # Make prediction
        predictions = ml_service.predict(model_data, input_df)
        
        return {
            "predictions": predictions.tolist(),
            "model_info": {
                "task_type": model.task_type,
                "algorithm": model.algorithm
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error making prediction: {str(e)}"
        ) 