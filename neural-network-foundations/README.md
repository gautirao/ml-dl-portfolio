# Neural Network From Scratch (NumPy)

A modular implementation of a dense neural network using only NumPy.

## 🧠 Intuitive Backpropagation

Imagine you're trying to hit a target with a complex Rube Goldberg machine.
1. **Forward Pass:** You drop the ball (input) and it rolls through the gears (layers). It lands somewhere (prediction).
2. **Loss:** You measure how far the ball landed from the target (the error).
3. **Backpropagation:** You work *backward* from the target:
   - "The final gear was too far right. Let's nudge it left."
   - "If I nudge that gear, how does the gear *before* it need to change?"
   - Each gear gets a small adjustment based on its contribution to the final error.

### The Math (Chain Rule)
For each layer, we calculate:
- **Output Gradient:** How much the error changes with respect to the output.
- **Weights Gradient:** How much the error changes with respect to the weights.
- **Input Gradient:** How much the error changes with respect to the input (passed to the previous layer).

## 📁 Project Structure
- `nn.py`: Core logic for `Layer`, `Sigmoid`, and `mse`.
- `train.py`: Training script for the XOR problem.
- `loss_curve.png`: Plot generated after training.

## 🚀 How to Run
1. Install dependencies: `pip install numpy matplotlib`
2. Run the training: `python train.py`
