import torch
from pydicom import dcmread
from PIL import Image
import torch.nn.functional as F
import torchvision.transforms as transforms

from .model import get_resnet18_model
from .data_loader import get_transforms

def predict_image(image_path, checkpoint_path):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 1. Load model and checkpoint
    model = get_resnet18_model(num_classes=2, pretrained=False)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.to(device)
    model.eval()
    
    # 2. Load and preprocess image
    image = dcmread(image_path).pixel_array
    image = image / 255.0
    
    # Handle both tensor and numpy cases
    if torch.is_tensor(image):
        image = (255 * image).clip(0, 255).type(torch.uint8).cpu().numpy()
    else:
        image = (255 * image).clip(0, 255).astype('uint8')
        
    image = Image.fromarray(image).convert('RGB')
    
    # Use inference transforms (Resize and ToTensor only)
    img_size = 224
    inference_transform = transforms.Compose([
        transforms.Resize(img_size),
        transforms.ToTensor()
    ])
    
    img_tensor = inference_transform(image).unsqueeze(0).to(device)
    
    # 3. Predict
    with torch.no_grad():
        outputs = model(img_tensor)
        probs = F.softmax(outputs, dim=1).squeeze(0).cpu().numpy()
        
    normal_prob = probs[0]
    pneumonia_prob = probs[1]
    
    prediction = "Normal" if normal_prob > pneumonia_prob else "Pneumonia"
    confidence = max(normal_prob, pneumonia_prob)
    
    print(f"Prediction: {prediction}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Probabilities:")
    print(f"  Normal: {normal_prob:.2f}")
    print(f"  Pneumonia: {pneumonia_prob:.2f}")
