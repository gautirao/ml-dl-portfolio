import pytest
from pathlib import Path
from src.ingestion.load_churn_data import load_churn_data
from src.features.preprocess import build_preprocessing_pipeline

def test_load_churn_data_missing_file():
    """Verify that a missing file triggers a SystemExit (via the load_churn_data helper)."""
    invalid_path = Path("non_existent_file.csv")
    with pytest.raises(SystemExit):
        load_churn_data(invalid_path)

def test_preprocessing_pipeline_creation():
    """Verify the pipeline can be created and has the correct steps."""
    pipeline = build_preprocessing_pipeline()
    assert "transformers" in dir(pipeline)
    
    # Check if we have 'num' and 'cat' transformers
    transformer_names = [t[0] for t in pipeline.transformers]
    assert "num" in transformer_names
    assert "cat" in transformer_names
