import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet18_Weights

def get_resnet18_model(num_classes=2, pretrained=True):
    """
    Returns a ResNet-18 model with the final fully connected layer 
    modified for the specified number of classes.
    """
    # Use the modern 'weights' API to avoid deprecation warnings
    weights = ResNet18_Weights.DEFAULT if pretrained else None
    model = models.resnet18(weights=weights)
    
    num_ftrs = model.fc.in_features
    # Modify the last layer (2 outputs: Pneumonia vs Normal)
    model.fc = nn.Linear(num_ftrs, num_classes)
    return model

