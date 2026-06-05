import os
import sys
import argparse
import subprocess

def run_script(script_path: str, args: list = []) -> bool:
    """Helper to run a python script as a subprocess and stream outputs."""
    cmd = [sys.executable, script_path] + args
    print(f"\n>>>> Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error executing script {script_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="SwiftETA ⭐: Predict. Optimize. Deliver. CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--generate", action="store_true", help="Generate the realistic synthetic dataset (6000 records)")
    parser.add_argument("--init-db", action="store_true", help="Initialize PostgreSQL/SQLite tables and seed reference data")
    parser.add_argument("--train", action="store_true", help="Train dual ML models (ETA Regressor + Delay Classifier), tune parameters, and compute SHAP")
    parser.add_argument("--run-app", action="store_true", help="Launch the Streamlit Operations & Predictions Dashboard")
    parser.add_argument("--all", action="store_true", help="Run the entire end-to-end pipeline (generate, init-db, train, and prepare models)")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any([args.generate, args.init_db, args.train, args.run_app, args.all]):
        parser.print_help()
        sys.exit(0)
        
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "app"))
    
    if args.all:
        print("================== RUNNING END-TO-END PIPELINE ==================")
        args.generate = True
        args.init_db = True
        args.train = True
        
    if args.generate:
        print("\n================== 1. DATA GENERATION STAGE ==================")
        script = os.path.join(src_dir, "generate_data.py")
        if not run_script(script):
            print("Pipeline aborted at Data Generation.")
            sys.exit(1)
            
    if args.init_db:
        print("\n================== 2. DATABASE INITIALIZATION STAGE ==================")
        script = os.path.join(src_dir, "db_helper.py")
        if not run_script(script):
            print("Pipeline aborted at Database Initialization.")
            sys.exit(1)
            
    if args.train:
        print("\n================== 3. MODEL TRAINING & EXPLAINABILITY ==================")
        script = os.path.join(src_dir, "train_model.py")
        if not run_script(script):
            print("Pipeline aborted at Model Training.")
            sys.exit(1)
            
    if args.run_app:
        print("\n================== 4. FRONTEND DASHBOARD LAUNCH STAGE ==================")
        app_script = os.path.join(app_dir, "streamlit_app.py")
        if not os.path.exists(app_script):
            print(f"Streamlit application file not found at: {app_script}")
            sys.exit(1)
            
        print("Spinning up local server. Press Ctrl+C in terminal to stop.")
        try:
            subprocess.run(["streamlit", "run", app_script])
        except KeyboardInterrupt:
            print("\nDashboard server stopped.")
        except Exception as e:
            print(f"Failed to launch Streamlit server: {e}")

if __name__ == "__main__":
    main()
