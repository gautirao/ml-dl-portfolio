import pandas as pd
import sys
from src.config import CHURN_DATA_FILE, TARGET_COL

def load_churn_data(file_path=CHURN_DATA_FILE):
    """Loads and performs initial validation of churn dataset."""
    if not file_path.exists():
        print(f"Error: Dataset not found at {file_path}")
        print("Please download it and place it in the data/raw/ directory.")
        sys.exit(1)

    df = pd.read_csv(file_path)

    if TARGET_COL not in df.columns:
        print(f"Error: Target column '{TARGET_COL}' missing from data.")
        sys.exit(1)

    print("--- Data Ingestion Summary ---")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()[:5]}... and more")
    print("\nMissing Values:")
    print(df.isnull().sum())
    
    return df

if __name__ == "__main__":
    load_churn_data()
