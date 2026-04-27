# RSNA Pneumonia Detection (Modular AI Project)

This project uses deep learning (ResNet-18) to identify pneumonia in chest X-ray images. It has been refactored from a Jupyter notebook into a modular, production-ready Python package with advanced visualization capabilities.

### 📁 Project Structure
```text
rsna-pneumonia-detection/
├── README.md
├── pyproject.toml
├── data/               # Project data (DICOM images & CSVs)
├── models/             # Saved model weights (.pth)
├── outputs/            # Visual prediction results (.png)
├── src/
│   └── rsna_pneumonia/
│       ├── cli.py          # CLI entry point
│       ├── data_loader.py  # Data handling & preprocessing
│       ├── model.py        # Model architecture
│       ├── trainer.py      # Training & validation logic
│       └── predict.py      # Inference & Visualization logic
└── tests/              # Unit tests
```

### 📋 Latest Features: The "Thinking Map" 🤖🎨
The Robot Doctor can now "show its work"! 
- **Visual Labels**: The prediction is written in big bold letters at the top of the X-ray.
- **Anomaly Detection (Grad-CAM)**: Even though it's a classifier, we use a "Heat Map" trick to see which parts of the lung made the robot think someone is sick.
- **Automatic Boxing**: The robot finds the "hottest" part of its heat map and draws a red square around it.
- **Image Export**: All results are saved as `.png` files in the `outputs/` folder.

---

### 🚀 Getting Started

#### 1. Setup Virtual Environment
```bash
cd pneumonia-detection-resnet
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

#### 2. Install the Project (Proper Way)
To ensure the `rsna_pneumonia` module is found by Python, install the project in "editable" mode:
```bash
pip install -e .
```

#### 3. Prepare Data
Ensure your RSNA dataset is in the `data/` folder.

---

### 🛠️ Commands

#### How do I train the model?
```bash
python -m rsna_pneumonia.cli train --epochs 10
```

#### How do I classify and VISUALIZE an X-ray?
```bash
python -m rsna_pneumonia.cli predict --image path/to/your_xray.dcm
```
**What happens?**
- The robot prints the result to your terminal.
- A new image with a **Red Box** and **Label** is saved in `pneumonia-detection-resnet/outputs/`.

#### How do I check accuracy?
```bash
python -m rsna_pneumonia.cli evaluate --checkpoint ./models/best_model.pth
```
**Interpretation**:
- **Accuracy**: <computed by evaluate>
- **Precision**: <computed by evaluate>
- **Recall**: <computed by evaluate>
- **F1-score**: <computed by evaluate>

---

### 🧪 Running Tests
To make sure the robot's brain is built correctly, you can run the model unit test:
```bash
# If installed via pip install -e .
python tests/test_model.py

# OR using pytest
pytest tests/
```

**⚠️ NOTE: The model is a classifier, not a true object detector. The boxes are generated using Grad-CAM heatmaps. Any accuracy numbers in sample outputs are examples only; run `evaluate` locally for real results.**
