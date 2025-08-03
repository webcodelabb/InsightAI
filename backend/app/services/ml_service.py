import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, classification_report, roc_auc_score
)
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from lazypredict.Supervised import LazyClassifier, LazyRegressor
import joblib
import os
import json
from typing import Dict, Any, Tuple, List
from datetime import datetime

class MLService:
    def __init__(self):
        self.models_dir = "./models"
        os.makedirs(self.models_dir, exist_ok=True)
    
    def prepare_data(self, df: pd.DataFrame, target_column: str, task_type: str) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """Prepare data for ML training."""
        # Remove target column from features
        feature_columns = [col for col in df.columns if col != target_column]
        
        # Handle missing values
        for col in feature_columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')
        
        # Encode categorical variables
        label_encoders = {}
        for col in feature_columns:
            if df[col].dtype == 'object':
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le
        
        # Prepare features and target
        X = df[feature_columns]
        y = df[target_column]
        
        # Encode target for classification
        if task_type == 'classification':
            target_encoder = LabelEncoder()
            y = target_encoder.fit_transform(y)
            label_encoders[target_column] = target_encoder
        
        return X, y, feature_columns, label_encoders
    
    def train_classification_model(self, df: pd.DataFrame, target_column: str, algorithm: str = 'auto') -> Dict[str, Any]:
        """Train a classification model."""
        X, y, feature_columns, label_encoders = self.prepare_data(df, target_column, 'classification')
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if algorithm == 'auto':
            # Use LazyPredict for automatic model selection
            clf = LazyClassifier(verbose=0, ignore_warnings=True, custom_metric=None)
            models, predictions = clf.fit(X_train_scaled, X_test_scaled, y_train, y_test)
            
            # Get best model
            best_model_name = models.index[0]
            best_model = clf.models[best_model_name]
            
            # Train best model on full dataset
            best_model.fit(X_train_scaled, y_train)
            y_pred = best_model.predict(X_test_scaled)
            y_pred_proba = best_model.predict_proba(X_test_scaled) if hasattr(best_model, 'predict_proba') else None
            
        else:
            # Use specific algorithm
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.svm import SVC
            
            if algorithm == 'random_forest':
                best_model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif algorithm == 'logistic_regression':
                best_model = LogisticRegression(random_state=42)
            elif algorithm == 'svm':
                best_model = SVC(probability=True, random_state=42)
            else:
                best_model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            best_model.fit(X_train_scaled, y_train)
            y_pred = best_model.predict(X_test_scaled)
            y_pred_proba = best_model.predict_proba(X_test_scaled) if hasattr(best_model, 'predict_proba') else None
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted')
        }
        
        if y_pred_proba is not None and len(np.unique(y_test)) == 2:
            metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba[:, 1])
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # Classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        metrics['classification_report'] = report
        
        return {
            'model': best_model,
            'scaler': scaler,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'metrics': metrics,
            'algorithm': algorithm if algorithm != 'auto' else best_model_name,
            'task_type': 'classification'
        }
    
    def train_regression_model(self, df: pd.DataFrame, target_column: str, algorithm: str = 'auto') -> Dict[str, Any]:
        """Train a regression model."""
        X, y, feature_columns, label_encoders = self.prepare_data(df, target_column, 'regression')
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if algorithm == 'auto':
            # Use LazyPredict for automatic model selection
            reg = LazyRegressor(verbose=0, ignore_warnings=True, custom_metric=None)
            models, predictions = reg.fit(X_train_scaled, X_test_scaled, y_train, y_test)
            
            # Get best model
            best_model_name = models.index[0]
            best_model = reg.models[best_model_name]
            
            # Train best model on full dataset
            best_model.fit(X_train_scaled, y_train)
            y_pred = best_model.predict(X_test_scaled)
            
        else:
            # Use specific algorithm
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.linear_model import LinearRegression
            from sklearn.svm import SVR
            
            if algorithm == 'random_forest':
                best_model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif algorithm == 'linear_regression':
                best_model = LinearRegression()
            elif algorithm == 'svr':
                best_model = SVR()
            else:
                best_model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            best_model.fit(X_train_scaled, y_train)
            y_pred = best_model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2_score': r2_score(y_test, y_pred)
        }
        
        return {
            'model': best_model,
            'scaler': scaler,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'metrics': metrics,
            'algorithm': algorithm if algorithm != 'auto' else best_model_name,
            'task_type': 'regression'
        }
    
    def train_clustering_model(self, df: pd.DataFrame, n_clusters: int = 3) -> Dict[str, Any]:
        """Train a clustering model."""
        # Prepare data (no target column for clustering)
        feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(feature_columns) < 2:
            raise ValueError("Need at least 2 numeric columns for clustering")
        
        X = df[feature_columns]
        
        # Handle missing values
        for col in feature_columns:
            X[col] = X[col].fillna(X[col].median())
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply PCA for visualization if many features
        if len(feature_columns) > 2:
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
        else:
            pca = None
            X_pca = X_scaled
        
        # Train clustering model
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Calculate metrics
        from sklearn.metrics import silhouette_score
        silhouette_avg = silhouette_score(X_scaled, clusters)
        
        metrics = {
            'silhouette_score': silhouette_avg,
            'n_clusters': n_clusters,
            'cluster_sizes': np.bincount(clusters).tolist()
        }
        
        return {
            'model': kmeans,
            'scaler': scaler,
            'pca': pca,
            'feature_columns': feature_columns,
            'metrics': metrics,
            'algorithm': 'kmeans',
            'task_type': 'clustering',
            'clusters': clusters.tolist(),
            'X_pca': X_pca.tolist()
        }
    
    def save_model(self, model_data: Dict[str, Any], model_name: str) -> str:
        """Save the trained model and related data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{model_name}_{timestamp}.joblib"
        model_path = os.path.join(self.models_dir, model_filename)
        
        # Save model and related data
        joblib.dump(model_data, model_path)
        
        return model_path
    
    def load_model(self, model_path: str) -> Dict[str, Any]:
        """Load a saved model."""
        return joblib.load(model_path)
    
    def predict(self, model_data: Dict[str, Any], new_data: pd.DataFrame) -> np.ndarray:
        """Make predictions using a trained model."""
        model = model_data['model']
        scaler = model_data['scaler']
        label_encoders = model_data['label_encoders']
        feature_columns = model_data['feature_columns']
        
        # Prepare new data
        X_new = new_data[feature_columns].copy()
        
        # Apply label encoding
        for col in feature_columns:
            if col in label_encoders:
                X_new[col] = label_encoders[col].transform(X_new[col].astype(str))
        
        # Scale features
        X_new_scaled = scaler.transform(X_new)
        
        # Make predictions
        predictions = model.predict(X_new_scaled)
        
        return predictions 