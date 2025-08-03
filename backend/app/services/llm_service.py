import openai
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import json

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        openai.api_key = self.api_key
        self.model = "gpt-4"
    
    def generate_insights(self, dataset_info: Dict[str, Any], model_results: Dict[str, Any]) -> str:
        """Generate AI-powered insights from dataset and model results."""
        
        # Prepare context for the LLM
        context = self._prepare_context(dataset_info, model_results)
        
        # Create the prompt
        prompt = self._create_insight_prompt(context)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data scientist and business analyst. Your role is to provide clear, actionable insights from machine learning model results and dataset analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def _prepare_context(self, dataset_info: Dict[str, Any], model_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context information for the LLM."""
        context = {
            "dataset": {
                "name": dataset_info.get("name", "Unknown"),
                "rows": dataset_info.get("row_count", 0),
                "columns": dataset_info.get("column_count", 0),
                "column_info": dataset_info.get("column_info", {}),
                "cleaning_report": dataset_info.get("cleaning_report", {})
            },
            "model": {
                "task_type": model_results.get("task_type", "unknown"),
                "algorithm": model_results.get("algorithm", "unknown"),
                "target_column": model_results.get("target_column", "unknown"),
                "feature_columns": model_results.get("feature_columns", []),
                "metrics": model_results.get("metrics", {}),
                "parameters": model_results.get("parameters", {})
            }
        }
        
        return context
    
    def _create_insight_prompt(self, context: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for insight generation."""
        
        dataset = context["dataset"]
        model = context["model"]
        
        prompt = f"""
        Analyze the following machine learning results and provide business-relevant insights:

        DATASET INFORMATION:
        - Name: {dataset['name']}
        - Size: {dataset['rows']} rows, {dataset['columns']} columns
        
        COLUMN ANALYSIS:
        """
        
        # Add column information
        for col_name, col_info in dataset['column_info'].items():
            prompt += f"\n- {col_name}:"
            prompt += f"\n  - Type: {col_info.get('type', 'unknown')}"
            prompt += f"\n  - Missing values: {col_info.get('missing_count', 0)} ({col_info.get('missing_percentage', 0):.1f}%)"
            prompt += f"\n  - Unique values: {col_info.get('unique_count', 0)}"
            
            if col_info.get('type') in ['integer', 'float']:
                prompt += f"\n  - Range: {col_info.get('min', 'N/A')} to {col_info.get('max', 'N/A')}"
                prompt += f"\n  - Mean: {col_info.get('mean', 'N/A')}"
                prompt += f"\n  - Std: {col_info.get('std', 'N/A')}"
        
        prompt += f"""

        MODEL INFORMATION:
        - Task Type: {model['task_type'].title()}
        - Algorithm: {model['algorithm']}
        - Target Variable: {model['target_column']}
        - Features Used: {', '.join(model['feature_columns'])}

        PERFORMANCE METRICS:
        """
        
        # Add performance metrics based on task type
        metrics = model['metrics']
        if model['task_type'] == 'classification':
            prompt += f"""
        - Accuracy: {metrics.get('accuracy', 'N/A'):.3f}
        - Precision: {metrics.get('precision', 'N/A'):.3f}
        - Recall: {metrics.get('recall', 'N/A'):.3f}
        - F1 Score: {metrics.get('f1_score', 'N/A'):.3f}
        """
            if 'roc_auc' in metrics:
                prompt += f"- ROC AUC: {metrics['roc_auc']:.3f}\n"
                
        elif model['task_type'] == 'regression':
            prompt += f"""
        - R² Score: {metrics.get('r2_score', 'N/A'):.3f}
        - RMSE: {metrics.get('rmse', 'N/A'):.3f}
        - MAE: {metrics.get('mae', 'N/A'):.3f}
        """
            
        elif model['task_type'] == 'clustering':
            prompt += f"""
        - Silhouette Score: {metrics.get('silhouette_score', 'N/A'):.3f}
        - Number of Clusters: {metrics.get('n_clusters', 'N/A')}
        - Cluster Sizes: {metrics.get('cluster_sizes', [])}
        """
        
        prompt += """

        Please provide:
        1. **Key Findings**: What are the most important insights from this analysis?
        2. **Model Performance**: How well does the model perform and what does this mean?
        3. **Feature Importance**: Which variables are most influential in the predictions?
        4. **Data Quality**: Any issues or patterns in the data that should be noted?
        5. **Business Recommendations**: What actionable insights can be derived?
        6. **Limitations**: What are the limitations of this analysis?
        7. **Next Steps**: What additional analysis would be valuable?

        Provide clear, business-friendly explanations that non-technical stakeholders can understand.
        """
        
        return prompt
    
    def generate_summary_report(self, dataset_info: Dict[str, Any], model_results: Dict[str, Any], insights: str) -> str:
        """Generate a comprehensive summary report."""
        
        context = self._prepare_context(dataset_info, model_results)
        
        prompt = f"""
        Create a professional executive summary report based on the following analysis:

        DATASET: {context['dataset']['name']}
        MODEL TYPE: {context['model']['task_type'].title()}
        ALGORITHM: {context['model']['algorithm']}

        INSIGHTS:
        {insights}

        Please create a structured report with:
        1. Executive Summary (2-3 sentences)
        2. Methodology Overview
        3. Key Findings
        4. Performance Analysis
        5. Recommendations
        6. Technical Details (brief)

        Format the report professionally for business presentation.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional data analyst creating executive reports. Write clearly and concisely for business stakeholders."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def generate_chart_descriptions(self, chart_data: Dict[str, Any]) -> str:
        """Generate descriptions for charts and visualizations."""
        
        prompt = f"""
        Analyze the following chart data and provide a clear description:

        Chart Type: {chart_data.get('type', 'unknown')}
        Data: {json.dumps(chart_data.get('data', {}), indent=2)}

        Please provide:
        1. What this chart shows
        2. Key patterns or trends
        3. Notable insights
        4. Business implications

        Write in clear, non-technical language.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data visualization expert explaining charts to business stakeholders."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating chart description: {str(e)}" 