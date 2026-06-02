import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor

# Add current directory (src/) to the module search paths to resolve sibling imports when called from parent directories
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import custom modules
from data_preprocessing import clean_and_process_file, get_preprocessor_pipeline
from feature_engineering import engineer_features
from evaluate_model import evaluate_regression, evaluate_classification

def load_and_engineer_data(raw_path="data/raw/deliveries.csv", processed_path="data/processed/processed_deliveries.csv"):
    """
    Cleans raw data, runs IQR outlier filtering, applies feature engineering,
    and returns a fully prepared pandas DataFrame.
    """
    # 1. Clean raw CSV and save processed file
    df_proc = clean_and_process_file(raw_path, processed_path)
    
    # 2. Apply feature engineering
    df_feat = engineer_features(df_proc)
    
    # 3. Create Classification Target (Is_Delayed)
    # Promised time = Prep Time + (Distance_km / 18.0) * 60 + 10 (overhead buffer)
    promised_time = df_feat["Preparation_Time"] + (df_feat["Distance_km"] / 18.0) * 60.0 + 8.0
    df_feat["Is_Delayed"] = (df_feat["Delivery_Time_Min"] > promised_time).astype(int)
    
    delay_pct = df_feat["Is_Delayed"].mean()
    print(f"Classification Label Created: {df_feat['Is_Delayed'].sum()} delayed out of {len(df_feat)} ({delay_pct:.1%})")
    
    return df_feat

def train_and_select_models():
    """
    Orchestrates the entire dual-model training, tuning, evaluation, and serialization pipeline.
    """
    df = load_and_engineer_data()
    
    # Define features and targets
    categorical_cols = [
        "Vehicle_Type", "Weather", "Traffic_Level", "Time_of_Day", 
        "Day_of_Week", "Festival_Day", "Holiday", "Order_Size", 
        "Customer_Location_Type", "Distance_Bucket"
    ]
    numerical_cols = [
        "Distance_km", "Preparation_Time", "Courier_Age", "Courier_Experience", 
        "Restaurant_Rating", "Traffic_Severity_Score", "Weather_Severity_Score",
        "is_peak_hour", "is_weekend", "is_night"
    ]
    
    features = categorical_cols + numerical_cols
    X = df[features]
    y_reg = df["Delivery_Time_Min"]
    y_clf = df["Is_Delayed"]
    
    # Train-test split
    X_train, X_test, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    _, _, y_train_clf, y_test_clf = train_test_split(X, y_clf, test_size=0.2, random_state=42)
    
    # Fit preprocessing pipeline
    print("\nFitting preprocessing pipeline...")
    preprocessor = get_preprocessor_pipeline(categorical_cols, numerical_cols)
    X_train_pre = preprocessor.fit_transform(X_train)
    X_test_pre = preprocessor.transform(X_test)
    
    # Save the fitted preprocessor immediately
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    with open(os.path.join(models_dir, "preprocessor.pkl"), "wb") as f:
        pickle.dump(preprocessor, f)
    print("Preprocessing pipeline fitted and saved successfully.")
    
    # ------------------ REGRESSION MODELS (ETA Prediction) ------------------
    print("\n================== REGRESSION MODEL TRAINING ==================")
    
    reg_models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=6, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42),
        "XGBoost Regressor": xgb.XGBRegressor(n_estimators=80, max_depth=5, learning_rate=0.1, random_state=42),
        "LightGBM Regressor": lgb.LGBMRegressor(n_estimators=80, max_depth=5, learning_rate=0.1, random_state=42, verbose=-1),
        "CatBoost Regressor": CatBoostRegressor(iterations=120, depth=5, learning_rate=0.1, random_seed=42, verbose=0)
    }
    
    reg_results = {}
    for name, model in reg_models.items():
        print(f"Training {name}...")
        model.fit(X_train_pre, y_train_reg)
        y_pred = model.predict(X_test_pre)
        metrics = evaluate_regression(y_test_reg, y_pred, name)
        reg_results[name] = {"model": model, "r2": metrics["R2_Score"], "mae": metrics["MAE"]}
        
    # --- Regression Hyperparameter Tuning (Random Forest) ---
    print("\nTuning hyperparameters for Random Forest...")
    rf_param_dist = {
        "n_estimators": [50, 100, 150],
        "max_depth": [6, 10, 15, None],
        "min_samples_split": [2, 5, 10]
    }
    rf_search = RandomizedSearchCV(
        RandomForestRegressor(random_state=42),
        param_distributions=rf_param_dist,
        n_iter=5,
        cv=3,
        scoring="neg_mean_absolute_error",
        random_state=42,
        n_jobs=-1
    )
    rf_search.fit(X_train_pre, y_train_reg)
    best_rf = rf_search.best_estimator_
    best_rf_pred = best_rf.predict(X_test_pre)
    rf_metrics = evaluate_regression(y_test_reg, best_rf_pred, "Tuned Random Forest")
    
    # Store tuned model
    reg_results["Tuned Random Forest"] = {"model": best_rf, "r2": rf_metrics["R2_Score"], "mae": rf_metrics["MAE"]}
    
    # Select Best Regressor (highest R2 Score)
    best_reg_name = max(reg_results, key=lambda k: reg_results[k]["r2"])
    best_regressor = reg_results[best_reg_name]["model"]
    print(f"\n>>>> Selected Best Regressor: {best_reg_name} (R2={reg_results[best_reg_name]['r2']:.4f})")
    
    # Save the best regressor pickle
    with open(os.path.join(models_dir, "best_regressor.pkl"), "wb") as f:
        pickle.dump(best_regressor, f)
        
    # ------------------ CLASSIFICATION MODELS (Delay Risk) ------------------
    print("\n================== CLASSIFICATION MODEL TRAINING ==================")
    
    clf_models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest Classifier": RandomForestClassifier(n_estimators=80, max_depth=8, random_state=42),
        "XGBoost Classifier": xgb.XGBClassifier(n_estimators=80, max_depth=5, learning_rate=0.1, eval_metric="logloss", random_state=42)
    }
    
    clf_results = {}
    for name, model in clf_models.items():
        print(f"Training {name}...")
        model.fit(X_train_pre, y_train_clf)
        y_pred = model.predict(X_test_pre)
        y_prob = model.predict_proba(X_test_pre)[:, 1]
        metrics = evaluate_classification(y_test_clf, y_pred, y_prob, name)
        clf_results[name] = {"model": model, "f1": metrics["F1_Score"], "acc": metrics["Accuracy"]}
        
    # Select Best Classifier (highest F1-Score)
    best_clf_name = max(clf_results, key=lambda k: clf_results[k]["f1"])
    best_classifier = clf_results[best_clf_name]["model"]
    print(f"\n>>>> Selected Best Classifier: {best_clf_name} (F1-Score={clf_results[best_clf_name]['f1']:.4f})")
    
    # Save the best classifier pickle
    with open(os.path.join(models_dir, "best_classifier.pkl"), "wb") as f:
        pickle.dump(best_classifier, f)
        
    # ------------------ SHAP EXPLAINABILITY ------------------
    print("\n================== COMPUTING SHAP EXPLAINER ==================")
    try:
        import shap
        # Train a light explainer on the best regression model
        # To make it fast and compatible with any model structure, we can fit a shap.Explainer
        # (for tree models TreeExplainer is extremely fast)
        
        # If it's a tree/ensemble, we use TreeExplainer or standard Explainer
        # To handle both linear, sklearn, and gradient boosted models safely, shap.Explainer is ideal
        # We pass a background sample of training set
        background_sample = shap.sample(X_train_pre, 100)
        
        print("Fitting SHAP Explainer...")
        explainer = shap.Explainer(best_regressor, background_sample)
        
        with open(os.path.join(models_dir, "shap_explainer.pkl"), "wb") as f:
            pickle.dump(explainer, f)
        print("SHAP explainer fitted and saved successfully.")
    except Exception as e:
        print(f"SHAP explainer generation failed: {e}. SHAP explanations will be computed dynamically.")
        
    print("\nAll models trained, evaluated, and saved successfully!")

if __name__ == "__main__":
    train_and_select_models()
