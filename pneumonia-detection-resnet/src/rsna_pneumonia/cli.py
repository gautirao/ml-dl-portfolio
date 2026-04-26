import os
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .data_loader import PneumoniaDataset, get_transforms, prepare_data
from .model import get_resnet18_model
from .trainer import train_one_epoch, validate
from .predict import predict_image

def train(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    print("Preparing data...")
    train_paths, train_labels, val_paths, val_labels, all_data = prepare_data(
        args.labels_csv, args.images_dir
    )

    transform = get_transforms()
    
    train_dataset = PneumoniaDataset(train_paths, train_labels, all_data, transform=transform)
    val_dataset = PneumoniaDataset(val_paths, val_labels, all_data, transform=transform)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    model = get_resnet18_model(pretrained=True).to(device)
    
    criterion = nn.CrossEntropyLoss()
    # Correcting optimizer to SGD to match original notebook evidence
    optimizer = torch.optim.SGD(model.parameters(), lr=args.lr, momentum=0.9)

    best_acc = 0.0
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch+1}/{args.epochs}")
        loss = train_one_epoch(model, train_loader, criterion, optimizer, device)
        acc, val_loss, prec, rec, f1, cm, total_samples = validate(model, val_loader, criterion, device)
        
        print(f"Train Loss: {loss:.4f}, Val Loss: {val_loss:.4f}, Validation Accuracy: {acc:.2f}%")
        
        if acc > best_acc:
            best_acc = acc
            os.makedirs(os.path.dirname(args.checkpoint), exist_ok=True)
            torch.save(model.state_dict(), args.checkpoint)
            print(f"New best model saved to {args.checkpoint}!")

def evaluate(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    print("Preparing validation data...")
    _, _, val_paths, val_labels, all_data = prepare_data(
        args.labels_csv, args.images_dir
    )
    
    transform = get_transforms()
    val_dataset = PneumoniaDataset(val_paths, val_labels, all_data, transform=transform)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    model = get_resnet18_model(pretrained=False).to(device)
    model.load_state_dict(torch.load(args.checkpoint, map_location=device))
    criterion = nn.CrossEntropyLoss()
    
    print("Evaluating...")
    acc, val_loss, prec, rec, f1, cm, total_samples = validate(model, val_loader, criterion, device)
    
    print("\n--- Evaluation Results ---")
    print(f"Total validation samples: {total_samples}")
    print(f"Validation Loss: {val_loss:.4f}")
    print(f"Accuracy: {acc:.2f}%")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)

def predict(args):
    predict_image(args.image, args.checkpoint)

def main():
    parser = argparse.ArgumentParser(description="Pneumonia Detection CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Train command
    parser_train = subparsers.add_parser("train", help="Train the model")
    parser_train.add_argument("--labels_csv", type=str, default="./data/stage_2_train_labels.csv", help="Path to labels CSV")
    parser_train.add_argument("--images_dir", type=str, default="./data/stage_2_train_images", help="Path to training images directory")
    parser_train.add_argument("--checkpoint", type=str, default="./models/best_model.pth", help="Path to save the best model")
    parser_train.add_argument("--batch_size", type=int, default=128, help="Batch size")
    parser_train.add_argument("--epochs", type=int, default=10, help="Training epochs")
    parser_train.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    
    # Evaluate command
    parser_eval = subparsers.add_parser("evaluate", help="Evaluate the model")
    parser_eval.add_argument("--labels_csv", type=str, default="./data/stage_2_train_labels.csv", help="Path to labels CSV")
    parser_eval.add_argument("--images_dir", type=str, default="./data/stage_2_train_images", help="Path to validation images directory")
    parser_eval.add_argument("--checkpoint", type=str, default="./models/best_model.pth", help="Path to the trained model checkpoint")
    parser_eval.add_argument("--batch_size", type=int, default=128, help="Batch size")
    
    # Predict command
    parser_pred = subparsers.add_parser("predict", help="Predict pneumonia from a single X-ray DICOM")
    parser_pred.add_argument("--image", type=str, required=True, help="Path to the DICOM image file")
    parser_pred.add_argument("--checkpoint", type=str, default="./models/best_model.pth", help="Path to the trained model checkpoint")

    args = parser.parse_args()
    
    if args.command == "train":
        train(args)
    elif args.command == "evaluate":
        evaluate(args)
    elif args.command == "predict":
        predict(args)

if __name__ == "__main__":
    main()
