import os
import pandas as pd
import numpy as np
from pydicom import dcmread
from PIL import Image
import torch
from torch.utils import data
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split

class PneumoniaDataset(data.Dataset):
    """Custom Dataset for RSNA Pneumonia Detection."""
    def __init__(self, paths, labels, all_data, transform=None):
        self.paths = paths
        self.labels = labels
        self.all_data = all_data
        self.transform = transform
    
    def __getitem__(self, index):
        # Read DICOM image
        image = dcmread(f'{self.paths[index]}.dcm')
        image = image.pixel_array
        image = image / 255.0

        # Convert to RGB for ResNet
        image = (255*image).clip(0, 255).astype(np.uint8)
        image = Image.fromarray(image).convert('RGB')

        label = self.labels[index][1]
        
        if self.transform is not None:
            image = self.transform(image)
        
        # Get bounding box if present
        name = self.paths[index].split("/")[-1]
        GH = self.all_data['patientId'] == name
        FIL = self.all_data[GH]
        box = [FIL['x'].values[0], FIL['y'].values[0], FIL['width'].values[0], FIL['height'].values[0]]
            
        return image, label, box
    
    def __len__(self):
        return len(self.paths)

def get_transforms(img_size=224):
    """Standard ResNet transformations."""
    return transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.Resize(img_size),
        transforms.ToTensor()
    ])

def prepare_data(labels_path, images_dir, test_size=0.1):
    """Loads labels and splits into train/val paths."""
    label_data = pd.read_csv(labels_path)
    all_data = label_data.copy()
    
    # Filter only patientId and Target for splitting
    labels_only = label_data[['patientId', 'Target']].values
    train_labels, val_labels = train_test_split(labels_only, test_size=test_size)
    
    train_paths = [os.path.join(images_dir, label[0]) for label in train_labels]
    val_paths = [os.path.join(images_dir, label[0]) for label in val_labels]
    
    return train_paths, train_labels, val_paths, val_labels, all_data
