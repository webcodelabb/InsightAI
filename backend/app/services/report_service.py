import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import fitz  # PyMuPDF
import os
from typing import Dict, Any, List
from datetime import datetime
import json

class ReportService:
    def __init__(self):
        self.reports_dir = "./reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_charts(self, model_data: Dict[str, Any], dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate charts for the report."""
        charts = {}
        
        task_type = model_data.get("task_type")
        metrics = model_data.get("metrics", {})
        
        if task_type == "classification":
            charts.update(self._generate_classification_charts(metrics))
        elif task_type == "regression":
            charts.update(self._generate_regression_charts(metrics))
        elif task_type == "clustering":
            charts.update(self._generate_clustering_charts(model_data))
        
        # Add dataset overview charts
        charts.update(self._generate_dataset_charts(dataset_info))
        
        return charts
    
    def _generate_classification_charts(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate classification-specific charts."""
        charts = {}
        
        # Confusion Matrix
        if 'confusion_matrix' in metrics:
            cm = metrics['confusion_matrix']
            fig = go.Figure(data=go.Heatmap(
                z=cm,
                x=['Predicted Negative', 'Predicted Positive'],
                y=['Actual Negative', 'Actual Positive'],
                colorscale='Blues',
                text=cm,
                texttemplate="%{text}",
                textfont={"size": 16}
            ))
            fig.update_layout(
                title="Confusion Matrix",
                xaxis_title="Predicted",
                yaxis_title="Actual"
            )
            charts['confusion_matrix'] = fig.to_html(full_html=False)
        
        # Metrics Bar Chart
        metric_names = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
        metric_values = [
            metrics.get('accuracy', 0),
            metrics.get('precision', 0),
            metrics.get('recall', 0),
            metrics.get('f1_score', 0)
        ]
        
        fig = go.Figure(data=go.Bar(
            x=metric_names,
            y=metric_values,
            marker_color='lightblue'
        ))
        fig.update_layout(
            title="Model Performance Metrics",
            yaxis_title="Score",
            yaxis_range=[0, 1]
        )
        charts['performance_metrics'] = fig.to_html(full_html=False)
        
        return charts
    
    def _generate_regression_charts(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate regression-specific charts."""
        charts = {}
        
        # Metrics Bar Chart
        metric_names = ['R² Score', 'RMSE', 'MAE']
        metric_values = [
            metrics.get('r2_score', 0),
            metrics.get('rmse', 0),
            metrics.get('mae', 0)
        ]
        
        fig = go.Figure(data=go.Bar(
            x=metric_names,
            y=metric_values,
            marker_color='lightgreen'
        ))
        fig.update_layout(
            title="Regression Model Performance",
            yaxis_title="Score"
        )
        charts['regression_metrics'] = fig.to_html(full_html=False)
        
        return charts
    
    def _generate_clustering_charts(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate clustering-specific charts."""
        charts = {}
        
        # Cluster Distribution
        if 'cluster_sizes' in model_data.get('metrics', {}):
            cluster_sizes = model_data['metrics']['cluster_sizes']
            cluster_labels = [f"Cluster {i}" for i in range(len(cluster_sizes))]
            
            fig = go.Figure(data=go.Pie(
                labels=cluster_labels,
                values=cluster_sizes,
                hole=0.3
            ))
            fig.update_layout(title="Cluster Distribution")
            charts['cluster_distribution'] = fig.to_html(full_html=False)
        
        # PCA Scatter Plot (if available)
        if 'X_pca' in model_data and 'clusters' in model_data:
            X_pca = model_data['X_pca']
            clusters = model_data['clusters']
            
            fig = go.Figure()
            for cluster_id in set(clusters):
                cluster_points = [i for i, c in enumerate(clusters) if c == cluster_id]
                fig.add_trace(go.Scatter(
                    x=[X_pca[i][0] for i in cluster_points],
                    y=[X_pca[i][1] for i in cluster_points],
                    mode='markers',
                    name=f'Cluster {cluster_id}',
                    marker=dict(size=8)
                ))
            
            fig.update_layout(
                title="Clusters Visualization (PCA)",
                xaxis_title="Principal Component 1",
                yaxis_title="Principal Component 2"
            )
            charts['clusters_visualization'] = fig.to_html(full_html=False)
        
        return charts
    
    def _generate_dataset_charts(self, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dataset overview charts."""
        charts = {}
        
        # Column Types Distribution
        column_info = dataset_info.get('column_info', {})
        type_counts = {}
        for col_info in column_info.values():
            col_type = col_info.get('type', 'unknown')
            type_counts[col_type] = type_counts.get(col_type, 0) + 1
        
        if type_counts:
            fig = go.Figure(data=go.Bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                marker_color='lightcoral'
            ))
            fig.update_layout(
                title="Column Types Distribution",
                xaxis_title="Data Type",
                yaxis_title="Count"
            )
            charts['column_types'] = fig.to_html(full_html=False)
        
        # Missing Values Chart
        missing_data = []
        for col_name, col_info in column_info.items():
            missing_percentage = col_info.get('missing_percentage', 0)
            if missing_percentage > 0:
                missing_data.append({
                    'column': col_name,
                    'missing_percentage': missing_percentage
                })
        
        if missing_data:
            fig = go.Figure(data=go.Bar(
                x=[d['column'] for d in missing_data],
                y=[d['missing_percentage'] for d in missing_data],
                marker_color='orange'
            ))
            fig.update_layout(
                title="Missing Values by Column",
                xaxis_title="Column",
                yaxis_title="Missing Percentage (%)"
            )
            charts['missing_values'] = fig.to_html(full_html=False)
        
        return charts
    
    def generate_pdf_report(self, model_data: Dict[str, Any], dataset_info: Dict[str, Any], insights: str) -> str:
        """Generate a comprehensive PDF report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"report_{timestamp}.pdf"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        # Generate charts
        charts = self.generate_charts(model_data, dataset_info)
        
        # Create PDF
        doc = fitz.open()
        page = doc.new_page()
        
        # Add title
        title = f"InsightAI Report - {dataset_info.get('name', 'Dataset')}"
        page.insert_text((50, 50), title, fontsize=24, color=(0, 0, 0))
        
        # Add timestamp
        timestamp_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        page.insert_text((50, 80), timestamp_text, fontsize=12, color=(100, 100, 100))
        
        # Add dataset information
        y_position = 120
        page.insert_text((50, y_position), "Dataset Information:", fontsize=16, color=(0, 0, 0))
        y_position += 30
        
        dataset_details = [
            f"Name: {dataset_info.get('name', 'Unknown')}",
            f"Rows: {dataset_info.get('row_count', 0):,}",
            f"Columns: {dataset_info.get('column_count', 0)}",
            f"Task Type: {model_data.get('task_type', 'Unknown').title()}",
            f"Algorithm: {model_data.get('algorithm', 'Unknown')}"
        ]
        
        for detail in dataset_details:
            page.insert_text((70, y_position), detail, fontsize=12, color=(0, 0, 0))
            y_position += 20
        
        # Add model metrics
        y_position += 20
        page.insert_text((50, y_position), "Model Performance:", fontsize=16, color=(0, 0, 0))
        y_position += 30
        
        metrics = model_data.get('metrics', {})
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)):
                page.insert_text((70, y_position), f"{metric_name.title()}: {metric_value:.3f}", fontsize=12, color=(0, 0, 0))
                y_position += 20
        
        # Add insights
        y_position += 20
        page.insert_text((50, y_position), "AI-Generated Insights:", fontsize=16, color=(0, 0, 0))
        y_position += 30
        
        # Split insights into paragraphs
        insight_paragraphs = insights.split('\n\n')
        for paragraph in insight_paragraphs[:3]:  # Limit to first 3 paragraphs
            if len(paragraph.strip()) > 0:
                # Wrap text to fit page width
                wrapped_text = self._wrap_text(paragraph, 80)
                for line in wrapped_text:
                    page.insert_text((70, y_position), line, fontsize=11, color=(0, 0, 0))
                    y_position += 15
                y_position += 10
        
        # Save PDF
        doc.save(report_path)
        doc.close()
        
        return report_path
    
    def generate_csv_results(self, model_data: Dict[str, Any], dataset_info: Dict[str, Any]) -> str:
        """Generate CSV results file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"results_{timestamp}.csv"
        csv_path = os.path.join(self.reports_dir, csv_filename)
        
        # Create results DataFrame
        results_data = {
            'Metric': [],
            'Value': [],
            'Description': []
        }
        
        # Add dataset information
        results_data['Metric'].extend(['Dataset Name', 'Row Count', 'Column Count', 'Task Type', 'Algorithm'])
        results_data['Value'].extend([
            dataset_info.get('name', 'Unknown'),
            dataset_info.get('row_count', 0),
            dataset_info.get('column_count', 0),
            model_data.get('task_type', 'Unknown'),
            model_data.get('algorithm', 'Unknown')
        ])
        results_data['Description'].extend([
            'Name of the analyzed dataset',
            'Number of rows in the dataset',
            'Number of columns in the dataset',
            'Type of machine learning task',
            'Algorithm used for training'
        ])
        
        # Add model metrics
        metrics = model_data.get('metrics', {})
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)):
                results_data['Metric'].append(metric_name.title())
                results_data['Value'].append(f"{metric_value:.4f}")
                results_data['Description'].append(f"{metric_name} score")
        
        # Create and save CSV
        df = pd.DataFrame(results_data)
        df.to_csv(csv_path, index=False)
        
        return csv_path
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_width:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines 