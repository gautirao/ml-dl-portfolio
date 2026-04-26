# RSNA Pneumonia Detection (Modular AI Project)

This project uses deep learning (ResNet-18) to identify pneumonia in chest X-ray images. It has been refactored from a Jupyter notebook into a modular, production-ready Python package.

### 📁 Project Structure
```text
rsna-pneumonia-detection/
├── README.md
├── requirements.txt
├── pyproject.toml
├── data/               # Project data (DICOM images & CSVs)
├── models/             # Directory for saved model weights
├── outputs/            # Directory for training outputs
├── src/
│   └── rsna_pneumonia/
│       ├── __init__.py
│       ├── cli.py          # CLI entry point
│       ├── data_loader.py  # Dataset handling & preprocessing
│       ├── model.py        # Model architecture
│       ├── trainer.py      # Training & validation logic
│       └── predict.py      # Inference logic
└── tests/              # Unit tests
```

### 📋 Original Notebook Logic vs Added Engineering Features
The core ML logic is strictly preserved from the original notebook, while the CLI and package structure are added for engineering robustness.

- **Preserved from Notebook**:
  - **Model**: Pre-trained ResNet18 with final layer modified to 2 outputs (`nn.Linear(num_ftrs, 2)`).
  - **Optimizer**: `torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)`.
  - **Batch Size**: `128`.
  - **Preprocessing**: `Resize(224)`, `RandomHorizontalFlip`, `ToTensor`.
  - **Loss**: `CrossEntropyLoss`.
  - **Data Splits**: 90% training / 10% validation.
  - **Progress Bars**: `tqdm` (originally used in the notebook training loops).
- **Preserved from Dataset Semantics**:
  - **Class Mapping**: `0 = Normal` (No lung opacity), `1 = Pneumonia` (Lung opacity).
- **Added Engineering Wrappers**:
  - **CLI**: `rsna-pneumonia` command with `train`, `evaluate`, and `predict` subparsers.
  - **Metrics**: Precision, Recall, F1, and Confusion Matrix (added to `evaluate` for deeper insight).
  - **Inference Pipeline**: `predict` logic that handles single `.dcm` files and outputs softmax probabilities.
  - **Package Structure**: Refactored into an installable Python package (`rsna_pneumonia`).

---

### 🚀 Getting Started

#### 1. Setup Virtual Environment
```bash
cd pneumonia-detection-resnet
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

#### 2. Install the Package
```bash
pip install -e .
```

#### 3. Prepare Data
Move your RSNA dataset into the `data/` folder:
- `data/stage_2_train_images/`
- `data/stage_2_train_labels.csv`

---

### 🛠️ Commands

#### How do I train the model?
```bash
python -m rsna_pneumonia.cli train --epochs 10 --lr 0.001
```
*(The best model is saved to `./models/best_model.pth` by default)*

#### How do I classify a single X-ray?
```bash
python -m rsna_pneumonia.cli predict --image path/to/xray.dcm --checkpoint ./models/best_model.pth
```
**Interpretation**:
- **Normal**: No lung opacities were detected (Class 0).
- **Pneumonia**: Lung opacities indicating pneumonia were detected (Class 1).
- **Confidence**: The model's "certainty" score.
- **Probabilities**: Raw model confidence for both outcomes.

#### How do I check accuracy?
```bash
python -m rsna_pneumonia.cli evaluate --checkpoint ./models/best_model.pth
```
**Interpretation**:
- **Accuracy**: <computed by evaluate>
- **Precision**: <computed by evaluate>
- **Recall**: <computed by evaluate>
- **F1-score**: <computed by evaluate>

The model is a classifier, not a true object detector. Bounding boxes, if present in the data, are for visualization and annotation, not predicted by this ResNet18 classifier. Any accuracy numbers in sample outputs are examples only; run `evaluate` locally for real results.
