import numpy as np
import matplotlib.pyplot as plt
from nn import Layer, Sigmoid, mse, mse_derivative

# 0. Reproducibility
np.random.seed(42)

# 1. Dataset (XOR Problem)
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
Y = np.array([[0], [1], [1], [0]])

# 2. Network Architecture
# Layer(2 inputs, 3 hidden) -> Sigmoid -> Layer(3 hidden, 1 output) -> Sigmoid
network = [
    Layer(2, 3),
    Sigmoid(),
    Layer(3, 1),
    Sigmoid()
]

# 3. Training Parameters
epochs = 10000
learning_rate = 0.5
losses = []

# 4. Training Loop
print("Training...")
for epoch in range(epochs):
    # Forward Pass
    output = X
    for layer in network:
        output = layer.forward(output)

    # Calculate Loss
    loss = mse(Y, output)
    losses.append(loss)

    # Backward Pass (Chain Rule in reverse order)
    gradient = mse_derivative(Y, output)
    for layer in reversed(network):
        gradient = layer.backward(gradient, learning_rate)

    if (epoch + 1) % 500 == 0:
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss:.6f}")

# 5. Testing
print("\nFinal Predictions:")
output = X
for layer in network:
    output = layer.forward(output)
print(output)

# 6. Plot Loss Curve
plt.figure(figsize=(8, 5))
plt.plot(losses)
plt.title('Training Loss over Epochs')
plt.xlabel('Epochs')
plt.ylabel('MSE Loss')
plt.grid(True)
plt.savefig('loss_curve.png')
print("\nLoss curve saved as 'loss_curve.png'")
plt.show()
