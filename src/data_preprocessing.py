import os
import pandas as pd
import numpy as np
import pickle
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans up missing values. If there are missing target values, drops them.
    Imputes numeric columns with their median and categoricals with their mode.
    """
    df_clean = df.copy()
    
    # Drop rows where target Delivery_Time_Min is missing
    if "Delivery_Time_Min" in df_clean.columns:
        df_clean = df_clean.dropna(subset=["Delivery_Time_Min"])
        
    for col in df_clean.columns:
        if df_clean[col].isnull().sum() > 0:
            if df_clean[col].dtype in [np.float64, np.int64]:
                median_val = df_clean[col].median()
                df_clean[col] = df_clean[col].fillna(median_val)
            else:
                mode_val = df_clean[col].mode()[0]
                df_clean[col] = df_clean[col].fillna(mode_val)
                
    return df_clean

def detect_and_filter_outliers_iqr(df: pd.DataFrame, columns: list, factor: float = 1.5) -> pd.DataFrame:
    """
    Identifies outliers using the IQR (Interquartile Range) method
    and filters them out of the dataset to prevent model distortion.
    """
    df_filtered = df.copy()
    initial_rows = len(df_filtered)
    
    for col in columns:
        if col in df_filtered.columns and df_filtered[col].dtype in [np.float64, np.int64]:
            q1 = df_filtered[col].quantile(0.25)
            q3 = df_filtered[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - (factor * iqr)
            upper_bound = q3 + (factor * iqr)
            
            # Filter rows within bounds
            df_filtered = df_filtered[(df_filtered[col] >= lower_bound) & (df_filtered[col] <= upper_bound)]
            
    removed_rows = initial_rows - len(df_filtered)
    print(f"IQR Outlier Filter: Removed {removed_rows} rows out of {initial_rows} ({removed_rows/initial_rows:.1%}) using factor={factor} across columns: {columns}")
    return df_filtered

def clean_and_process_file(raw_path: str, processed_path: str) -> pd.DataFrame:
    """
    Orchestrates the data cleaning pipeline:
    1. Loads raw dataset
    2. Handles missing values
    3. Detects and filters outliers via IQR on distance, prep time, and delivery time
    4. Saves the resulting processed CSV.
    """
    print(f"Loading raw deliveries from: {raw_path}")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found at: {raw_path}")
        
    df = pd.read_csv(raw_path)
    
    # 1. Clean missing values
    df_clean = handle_missing_values(df)
    
    # 2. Outlier Analysis (on continuous numeric variables)
    outlier_cols = ["Distance_km", "Preparation_Time", "Delivery_Time_Min"]
    df_processed = detect_and_filter_outliers_iqr(df_clean, outlier_cols, factor=1.5)
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df_processed.to_csv(processed_path, index=False)
    print(f"Cleaned and saved processed dataset with {len(df_processed)} rows to: {processed_path}")
    return df_processed

def get_preprocessor_pipeline(categorical_cols: list, numerical_cols: list) -> ColumnTransformer:
    """
    Generates a fitted ColumnTransformer pipeline that normalizes numerical columns
    with StandardScaler and encodes categorical columns with OneHotEncoder.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols)
        ]
    )
    return preprocessor

if __name__ == "__main__":
    # Test preprocessor logic
    raw_csv = "data/raw/deliveries.csv"
    processed_csv = "data/processed/processed_deliveries.csv"
    
    if os.path.exists(raw_csv):
        clean_and_process_file(raw_csv, processed_csv)
    else:
        print(f"Raw CSV not found at {raw_csv}. Please run generate_data.py first.")
