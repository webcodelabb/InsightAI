from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from typing import Dict, Any

from app.models.database import get_db
from app.models.user import User
from app.models.dataset import Model, Dataset
from app.utils.auth import get_current_active_user
from app.services.report_service import ReportService
from app.services.ml_service import MLService
from app.services.llm_service import LLMService

router = APIRouter()
report_service = ReportService()
ml_service = MLService()
llm_service = LLMService()

@router.get("/{model_id}/pdf")
async def download_pdf_report(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download PDF report for a model."""
    # Get the model
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
        # Load model data
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
        
        # Generate PDF report
        pdf_path = report_service.generate_pdf_report(
            model_data, dataset_info, insights
        )
        
        # Return the PDF file
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=f"insightai_report_{model.name}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF report: {str(e)}"
        )

@router.get("/{model_id}/csv")
async def download_csv_results(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download CSV results for a model."""
    # Get the model
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
        # Load model data
        model_data = ml_service.load_model(model.model_path)
        
        # Get dataset info
        dataset = db.query(Dataset).filter(Dataset.id == model.dataset_id).first()
        
        dataset_info = {
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "column_info": dataset.column_info
        }
        
        # Generate CSV results
        csv_path = report_service.generate_csv_results(model_data, dataset_info)
        
        # Return the CSV file
        return FileResponse(
            path=csv_path,
            media_type='text/csv',
            filename=f"insightai_results_{model.name}.csv"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating CSV results: {str(e)}"
        )

@router.get("/{model_id}/charts")
async def get_model_charts(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get charts and visualizations for a model."""
    # Get the model
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
        # Load model data
        model_data = ml_service.load_model(model.model_path)
        
        # Get dataset info
        dataset = db.query(Dataset).filter(Dataset.id == model.dataset_id).first()
        
        dataset_info = {
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "column_info": dataset.column_info
        }
        
        # Generate charts
        charts = report_service.generate_charts(model_data, dataset_info)
        
        return {
            "model_id": model_id,
            "charts": charts,
            "model_info": {
                "task_type": model.task_type,
                "algorithm": model.algorithm,
                "target_column": model.target_column
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating charts: {str(e)}"
        )

@router.get("/{model_id}/summary")
async def get_model_summary(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a comprehensive summary report for a model."""
    # Get the model
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
        # Load model data
        model_data = ml_service.load_model(model.model_path)
        
        # Get dataset info
        dataset = db.query(Dataset).filter(Dataset.id == model.dataset_id).first()
        
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
        
        # Generate insights
        insights = llm_service.generate_insights(dataset_info, model_results)
        
        # Generate summary report
        summary = llm_service.generate_summary_report(dataset_info, model_results, insights)
        
        return {
            "model_id": model_id,
            "insights": insights,
            "summary": summary,
            "metrics": model.metrics,
            "dataset_info": dataset_info,
            "model_info": {
                "task_type": model.task_type,
                "algorithm": model.algorithm,
                "target_column": model.target_column,
                "feature_columns": model.feature_columns
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        ) 