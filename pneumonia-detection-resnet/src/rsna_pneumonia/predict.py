import os
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from pydicom import dcmread
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from .model import get_resnet18_model

def predict_image(image_path, checkpoint_path, output_dir="./outputs"):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    os.makedirs(output_dir, exist_ok=True)

    # 1. Build the Robot Brain and load its memories
    model = get_resnet18_model(num_classes=2, pretrained=False)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.to(device)
    model.eval()

    # 2. Open the hospital picture
    ds = dcmread(image_path)
    image_np = ds.pixel_array
    
    # Clean the picture for the robot
    img_normalized = image_np / 255.0
    img_rgb = Image.fromarray((img_normalized * 255).astype(np.uint8)).convert('RGB')
    
    # Prep the picture (Resize to 224 like training)
    img_size = 224
    transform = transforms.Compose([
        transforms.Resize(img_size),
        transforms.ToTensor()
    ])
    input_tensor = transform(img_rgb).unsqueeze(0).to(device)

    # 3. Use the "Thinking Map" (Grad-CAM)
    # We want to see what the last "looking" layer (layer4) is thinking
    features = []
    def hook_feature(module, input, output):
        features.append(output)
    
    handle = model.layer4.register_forward_hook(hook_feature)

    # Ask the robot what it thinks
    input_tensor.requires_grad = True
    outputs = model(input_tensor)
    probs = F.softmax(outputs, dim=1).squeeze(0)
    
    # Get the answer
    pred_idx = torch.argmax(probs).item()
    confidence = probs[pred_idx].item()
    label = "Normal" if pred_idx == 0 else "Pneumonia"
    
    # If it's pneumonia, find where the boo-boo is
    bbox = None
    if label == "Pneumonia":
        # Backwards logic to find the 'heat'
        model.zero_grad()
        class_loss = outputs[0, pred_idx]
        class_loss.backward()
        
        # Get the 'thinking weights'
        grads = model.layer4[1].conv2.weight.grad
        pooled_grads = torch.mean(grads, dim=[0, 2, 3])
        
        # Multiply the map by how important each part was
        for i in range(512):
            features[0][0, i, :, :] *= pooled_grads[i]
            
        heatmap = torch.mean(features[0], dim=1).squeeze()
        heatmap = F.relu(heatmap)
        heatmap /= torch.max(heatmap)
        heatmap_np = heatmap.detach().cpu().numpy()
        
        # Find the box from the heat (find where it's hottest)
        # We look for pixels with > 50% heat
        y, x = np.where(heatmap_np > 0.5)
        if len(x) > 0 and len(y) > 0:
            # Map back to original image size (1024x1024 usually)
            h_orig, w_orig = image_np.shape
            scale_x = w_orig / heatmap_np.shape[1]
            scale_y = h_orig / heatmap_np.shape[0]
            
            x_min, x_max = x.min() * scale_x, x.max() * scale_x
            y_min, y_max = y.min() * scale_y, y.max() * scale_y
            bbox = [x_min, y_min, x_max - x_min, y_max - y_min]

    handle.remove()

    # 4. Draw and Save the results
    fig, ax = plt.subplots(1, figsize=(8, 8))
    ax.imshow(image_np, cmap='gray')
    
    # Write the answer on top
    color = 'red' if label == "Pneumonia" else 'green'
    title_text = f"Prediction: {label} ({confidence:.2%})"
    plt.title(title_text, fontsize=16, color=color, fontweight='bold')
    
    # Draw the box if we found one
    if bbox:
        rect = patches.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3], 
                                linewidth=3, edgecolor='red', facecolor='none')
        ax.add_patch(rect)
        ax.text(bbox[0], bbox[1]-10, 'Anomaly Area', color='red', fontweight='bold')

    plt.axis('off')
    
    # Save the file
    filename = os.path.basename(image_path).replace('.dcm', '_prediction.png')
    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

    # Print text summary to screen
    print(f"Prediction: {label}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Result image saved to: {save_path}")
