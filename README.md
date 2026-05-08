# ML & DL Portfolio

Welcome to my Machine Learning and Deep Learning portfolio. This repository contains various exercises and projects that demonstrate different aspects of the ML/DL lifecycle, from foundations to explainable pipelines.

## 📂 Project Structure

### 1. [Explainable Regression Pipeline](./explainable-regression-pipeline/)
**The "Robot Guessing Game"**
A clean-coded, modular pipeline for predicting battery capacity using the **Extra Trees Regressor**.
- **Key Concepts:** Feature scaling, Cross-validation, Model Evaluation (RMSE, MAE, R2), and Model Interpretability using **SHAP**.
- **Use Case:** Predicting battery energy capacity from manufacturing parameters.

### 2. [Neural Network Foundations](./neural-network-foundations/)
**The "Rube Goldberg Machine"**
A modular implementation of a dense neural network built from scratch using only **NumPy**.
- **Key Concepts:** Forward propagation, Backpropagation (Chain Rule), Loss functions, and Gradient Descent.
- **Use Case:** Solving the XOR problem to demonstrate foundational deep learning mechanics.

### 3. [ML Support & Ops Platform](./ml-support-ops-platform/)
A more structured and comprehensive MLOps-style project with clear separation of concerns.
- **Key Concepts:** Data ingestion, feature preprocessing, model training, evaluation, and reporting.
- **Structure:** `src/` for core logic, `data/` for raw/processed data, `models/` for saved model binaries, and `reports/` for visualization outputs.

### 4. [Pneumonia Detection (Modular AI Project)](./pneumonia-detection-resnet/)
**The "Robot Doctor"**
A production-ready deep learning package for classifying chest X-rays to detect pneumonia using **ResNet-18**.
- **Key Concepts:** Computer Vision, Transfer Learning, DICOM image processing, modular CLI (Train/Evaluate/Predict), and detailed performance metrics (Precision, Recall, F1).
- **Use Case:** Identifying "lung opacities" in medical radiographs from the RSNA Pneumonia Detection Challenge.

### 5. [LedgerMind Local](./ledgermind-local/)
**The "Trust-but-Verify" AI Accountant**
A privacy-first, local-AI financial assistant that uses a **Planner-Executor architecture** to analyze bank statements without data leaving the user's machine.
- **Key Concepts:** Planner-Executor Pattern, Local LLM (Ollama/llama3.2), Deterministic SQL Execution (DuckDB), Local RAG for system explanations, Human-in-the-Loop Categorization, and Evidence-Based AI (Execution Trace).
- **Use Case:** Securely analyzing personal spending patterns while ensuring 100% numerical accuracy through deterministic calculations instead of LLM arithmetic.

---

## 🚀 How to Get Started

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ml-dl-portfolio
   ```

2. **Explore a project:**
   Each folder contains its own `requirements.txt` (if applicable) and its own `README.md` with specific execution instructions.

3. **Install Dependencies:**
   It is recommended to use virtual environments for each project.
   ```bash
   # Example for Explainable Regression Pipeline
   cd explainable-regression-pipeline
   pip install -r requirements.txt
   ```

---

*This portfolio is designed to showcase clear documentation, clean code practices, and a deep understanding of machine learning principles.*
