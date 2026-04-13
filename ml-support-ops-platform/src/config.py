from src.utils.paths import RAW_DATA_PATH

CHURN_DATA_FILE = RAW_DATA_PATH / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

# Column names
TARGET_COL = "Churn"
ID_COL = "customerID"

# Feature definitions
CATEGORICAL_FEATURES = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService',
    'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
    'Contract', 'PaperlessBilling', 'PaymentMethod'
]

NUMERICAL_FEATURES = ['tenure', 'MonthlyCharges', 'TotalCharges']
