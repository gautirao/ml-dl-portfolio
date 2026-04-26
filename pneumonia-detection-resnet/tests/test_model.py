import sys
import os
import torch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from model import get_resnet18_model

def test_model_output_shape():
    """Test if model outputs the correct shape for 2 classes."""
    model = get_resnet18_model(num_classes=2, pretrained=False)
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    assert output.shape == (1, 2), f"Expected shape (1, 2), got {output.shape}"

if __name__ == "__main__":
    test_model_output_shape()
    print("Model test passed!")
