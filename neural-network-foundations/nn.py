import numpy as np

class Layer:
    """A single dense (fully connected) layer."""
    def __init__(self, input_size, output_size):
        # Xavier initialization: Standard Deviation of sqrt(1/input_size)
        self.weights = np.random.randn(input_size, output_size) * np.sqrt(1 / input_size)
        self.biases = np.zeros((1, output_size))
        self.input = None
        self.output = None

    def forward(self, input_data):
        """Computes the linear part: z = xW + b"""
        self.input = input_data
        self.output = np.dot(self.input, self.weights) + self.biases
        return self.output

    def backward(self, output_gradient, learning_rate):
        """Updates weights/biases and returns the gradient for the previous layer."""
        weights_gradient = np.dot(self.input.T, output_gradient)
        input_gradient = np.dot(output_gradient, self.weights.T)

        # Gradient descent step
        self.weights -= learning_rate * weights_gradient
        self.biases -= learning_rate * np.sum(output_gradient, axis=0, keepdims=True)

        return input_gradient

class Sigmoid:
    """Sigmoid activation function: 1 / (1 + e^-x)"""
    def forward(self, input_data):
        self.input = input_data
        self.output = 1 / (1 + np.exp(-self.input))
        return self.output

    def backward(self, output_gradient, learning_rate):
        """Derivative of sigmoid: sigmoid(x) * (1 - sigmoid(x))"""
        sigmoid_derivative = self.output * (1 - self.output)
        return output_gradient * sigmoid_derivative

def mse(y_true, y_pred):
    """Mean Squared Error: (1/n) * sum((y_true - y_pred)^2)"""
    return np.mean(np.power(y_true - y_pred, 2))

def mse_derivative(y_true, y_pred):
    """Derivative of MSE with respect to y_pred: (2/n) * (y_pred - y_true)"""
    return 2 * (y_pred - y_true) / y_true.size
