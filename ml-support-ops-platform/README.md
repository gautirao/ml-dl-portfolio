# ML Support Ops Platform - Week 2

## Purpose
A local-first ML project focused on customer churn prediction using the Telco dataset. Week 2 extends the project with advanced evaluation, feature importance inspection, and additional baseline models.

## Setup Instructions (MacBook M1)

1. **Create and Activate Environment**
   ```bash
   cd ml-support-ops-platform
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Prepare Data**
   The project includes the [Telco Churn Dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) in `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`.

4. **Launch Jupyter Lab**
   ```bash
   jupyter lab
   ```

## Running Scripts

- **Full Model Training & Evaluation:**
  ```bash
  export PYTHONPATH=$PYTHONPATH:$(pwd)
  python src/training/train_churn.py
  ```
  This script will train both Logistic Regression and Random Forest models, saving artifacts and evaluation plots to `models/` and `reports/`.

- **Run Tests:**
  ```bash
  export PYTHONPATH=$PYTHONPATH:$(pwd)
  pytest tests
  ```

## Week 2 Enhancements
- [x] **Stronger Evaluation:** Added ROC-AUC, classification reports, and confusion matrix visualizations.
- [x] **Feature Importance:** Automated extraction and visualization of top 20 features for both models.
- [x] **Baseline Models:** Added Random Forest for comparison against Logistic Regression.
- [x] **Improved Reports:** All metrics and plots are automatically saved to the `reports/` directory.
- [x] **Expanded Testing:** Added specific tests for preprocessing and evaluation logic.

## Project Roadmap
- [x] Week 1: Local setup, Data ingestion, Baseline model.
- [x] Week 2: Stronger evaluation, Feature importance, Random Forest comparison.
- [ ] Week 3: Support Ticket NLP (Planned)
- [ ] Week 4: Deployment Prototype (Planned)
