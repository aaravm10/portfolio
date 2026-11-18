import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# loading and preparing data
data = pd.read_csv('data/train.csv')

# converting data to numpy array (for math calculations)
data = np.array(data)
m, n = data.shape # m = # of rows (images in dataset), n = 1 + # of columns (label + pixels in image) - 42000, 785
np.random.shuffle(data) # shuffle before splitting into dev and training sets

# dev set for model testing (first 1000 images)
data_dev = data[0:1000].T
Y_dev = data_dev[0] # labels for dev set
X_dev = data_dev[1:n] # pixels for dev set
X_dev = X_dev / 255. # normalizing pixel values to be between 0 and 1 (originally 0-255)

# training set for model training (last 41000 images)
data_train = data[1000:m].T
Y_train = data_train[0] # labels for training set
X_train = data_train[1:n] # pixels for training set
X_train = X_train / 255.
_,m_train = X_train.shape

Y_train

# initialize layer weights and biases
def init_params():
    # layer 1: 128 neurons (activation values) , 784 inputs (pixels of image) 
    W1 = np.random.rand(128, 784) - 0.5
    b1 = np.random.rand(128, 1) - 0.5

    # layer 2: 64 neurons (activation values), 128 inputs (from layer 1)
    W2 = np.random.rand(64, 128) - 0.5
    b2 = np.random.rand(64, 1) - 0.5

    # final layer: 10 neurons (activation values), 64 inputs (from layer 1)
    W3 = np.random.rand(10, 64) - 0.5
    b3 = np.random.rand(10, 1) - 0.5
    
    return W1, b1, W2, b2, W3, b3


# activation functions
def ReLU(Z):
    return np.maximum(Z, 0)

def ReLU_deriv(Z):
    return Z > 0

def softmax(Z):
    A = np.exp(Z) / sum(np.exp(Z))
    return A

def leaky_ReLU(Z):
    return np.where(Z > 0, Z, 0.01 * Z)

def leaky_ReLU_deriv(Z):
    return np.where(Z > 0, 1, 0.01)

# forward propagation - passing images through layers to get activation values
def forward_prop(W1, b1, W2, b2, W3, b3, X):
    Z1 = W1.dot(X) + b1
    A1 = leaky_ReLU(Z1)
    Z2 = W2.dot(A1) + b2
    A2 = leaky_ReLU(Z2)
    Z3 = W3.dot(A2) + b3
    A3 = softmax(Z3)
    return Z1, A1, Z2, A2, Z3, A3

# back prop
def one_hot(Y):
    one_hot_Y = np.zeros((Y.size, Y.max() + 1))
    one_hot_Y[np.arange(Y.size), Y] = 1
    one_hot_Y = one_hot_Y.T
    return one_hot_Y

def backward_prop(Z1, A1, Z2, A2, Z3, A3, W1, W2, W3, X, Y):
    one_hot_Y = one_hot(Y)

    # final layer inaccuracy
    dZ3 = A3 - one_hot_Y                          
    dW3 = 1 / m * dZ3.dot(A2.T)                   
    db3 = 1 / m * np.sum(dZ3)

    # layer 2 inaccuracy
    dZ2 = W3.T.dot(dZ3) * leaky_ReLU_deriv(Z2)          
    dW2 = 1 / m * dZ2.dot(A1.T)
    db2 = 1 / m * np.sum(dZ2)

    # first layer inaccuracy
    dZ1 = W2.T.dot(dZ2) * leaky_ReLU_deriv(Z1)          
    dW1 = 1 / m * dZ1.dot(X.T)
    db1 = 1 / m * np.sum(dZ1)

    return dW1, db1, dW2, db2, dW3, db3


def init_adam(W1, b1, W2, b2, W3, b3):
    m_W1 = np.zeros_like(W1)
    v_W1 = np.zeros_like(W1)
    m_b1 = np.zeros_like(b1)
    v_b1 = np.zeros_like(b1)
    m_W2 = np.zeros_like(W2)
    v_W2 = np.zeros_like(W2)
    m_b2 = np.zeros_like(b2)
    v_b2 = np.zeros_like(b2)
    m_W3 = np.zeros_like(W3)
    v_W3 = np.zeros_like(W3)
    m_b3 = np.zeros_like(b3)
    v_b3 = np.zeros_like(b3)
    return m_W1, v_W1, m_b1, v_b1, m_W2, v_W2, m_b2, v_b2, m_W3, v_W3, m_b3, v_b3

def update_params_adam(W1, b1, W2, b2, W3, b3,
                        dW1, db1, dW2, db2, dW3, db3,
                        m_W1, v_W1, m_b1, v_b1,
                        m_W2, v_W2, m_b2, v_b2,
                        m_W3, v_W3, m_b3, v_b3,
                        t, alpha=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):

    # Update biased moment estimates for each parameter
    m_W1 = beta1 * m_W1 + (1 - beta1) * dW1
    v_W1 = beta2 * v_W1 + (1 - beta2) * dW1**2
    m_b1 = beta1 * m_b1 + (1 - beta1) * db1
    v_b1 = beta2 * v_b1 + (1 - beta2) * db1**2

    m_W2 = beta1 * m_W2 + (1 - beta1) * dW2
    v_W2 = beta2 * v_W2 + (1 - beta2) * dW2**2
    m_b2 = beta1 * m_b2 + (1 - beta1) * db2
    v_b2 = beta2 * v_b2 + (1 - beta2) * db2**2

    m_W3 = beta1 * m_W3 + (1 - beta1) * dW3
    v_W3 = beta2 * v_W3 + (1 - beta2) * dW3**2
    m_b3 = beta1 * m_b3 + (1 - beta1) * db3
    v_b3 = beta2 * v_b3 + (1 - beta2) * db3**2

    # Bias correction — prevents steps being too small early in training
    m_W1_corr = m_W1 / (1 - beta1**t)
    v_W1_corr = v_W1 / (1 - beta2**t)
    m_b1_corr = m_b1 / (1 - beta1**t)
    v_b1_corr = v_b1 / (1 - beta2**t)

    m_W2_corr = m_W2 / (1 - beta1**t)
    v_W2_corr = v_W2 / (1 - beta2**t)
    m_b2_corr = m_b2 / (1 - beta1**t)
    v_b2_corr = v_b2 / (1 - beta2**t)

    m_W3_corr = m_W3 / (1 - beta1**t)
    v_W3_corr = v_W3 / (1 - beta2**t)
    m_b3_corr = m_b3 / (1 - beta1**t)
    v_b3_corr = v_b3 / (1 - beta2**t)

    # Update weights
    W1 -= alpha * m_W1_corr / (np.sqrt(v_W1_corr) + epsilon)
    b1 -= alpha * m_b1_corr / (np.sqrt(v_b1_corr) + epsilon)
    W2 -= alpha * m_W2_corr / (np.sqrt(v_W2_corr) + epsilon)
    b2 -= alpha * m_b2_corr / (np.sqrt(v_b2_corr) + epsilon)
    W3 -= alpha * m_W3_corr / (np.sqrt(v_W3_corr) + epsilon)
    b3 -= alpha * m_b3_corr / (np.sqrt(v_b3_corr) + epsilon)

    return (W1, b1, W2, b2, W3, b3,
            m_W1, v_W1, m_b1, v_b1,
            m_W2, v_W2, m_b2, v_b2,
            m_W3, v_W3, m_b3, v_b3)


def get_predictions(A3):
    return np.argmax(A3, 0)

def get_accuracy(predictions, Y):
    print(predictions, Y)
    return np.sum(predictions == Y) / Y.size

# training loop 
def gradient_descent(X, Y, alpha, epochs, batch_size=64):
    W1, b1, W2, b2, W3, b3 = init_params()
    m_W1, v_W1, m_b1, v_b1, m_W2, v_W2, m_b2, v_b2, m_W3, v_W3, m_b3, v_b3 = init_adam(W1, b1, W2, b2, W3, b3)
    
    m_train = X.shape[1]  # total number of training images
    t = 0                 # adam timestep, needs to increment across batches

    # mini-batch gradient descent
    for epoch in range(epochs):
        # shuffle data
        indices = np.random.permutation(m_train)
        X_shuffled = X[:, indices]
        Y_shuffled = Y[indices]
    
        
        for i in range(0, m_train, batch_size):
            # grab current batch
            X_batch = X_shuffled[:, i:i+batch_size]
            Y_batch = Y_shuffled[i:i+batch_size]

            t += 1  # increment adam timestep
            Z1, A1, Z2, A2, Z3, A3 = forward_prop(W1, b1, W2, b2, W3, b3, X)
            dW1, db1, dW2, db2, dW3, db3 = backward_prop(Z1, A1, Z2, A2, Z3, A3, W1, W2, W3, X, Y)
            (W1, b1, W2, b2, W3, b3,
            m_W1, v_W1, m_b1, v_b1,
            m_W2, v_W2, m_b2, v_b2,
            m_W3, v_W3, m_b3, v_b3) = update_params_adam(
                W1, b1, W2, b2, W3, b3,
                dW1, db1, dW2, db2, dW3, db3,
                m_W1, v_W1, m_b1, v_b1,
                m_W2, v_W2, m_b2, v_b2,
                m_W3, v_W3, m_b3, v_b3,
                t, alpha=alpha)

        # print accuracy every epoch
        _, _, _, _, _, A3_full = forward_prop(W1, b1, W2, b2, W3, b3, X)
        predictions = get_predictions(A3_full)
        print(f"Epoch {epoch} | Accuracy: {get_accuracy(predictions, Y):.4f}")

    return W1, b1, W2, b2, W3, b3


W1, b1, W2, b2, W3, b3 = gradient_descent(X_train, Y_train, 0.0005, 10)


def make_predictions(X, W1, b1, W2, b2, W3, b3):
    _, _, _, A2, _, A3 = forward_prop(W1, b1, W2, b2, W3, b3, X)
    predictions = get_predictions(A3)
    return predictions

def test_prediction(index, W1, b1, W2, b2, W3, b3):
    current_image = X_train[:, index, None]
    prediction = make_predictions(X_train[:, index, None], W1, b1, W2, b2, W3, b3)
    label = Y_train[index]
    print("Prediction: ", prediction)
    print("Label: ", label)
    
    current_image = current_image.reshape((28, 28)) * 255
    plt.gray()
    plt.imshow(current_image, interpolation='nearest')
    plt.show()


test_prediction(0, W1, b1, W2, b2, W3, b3)
test_prediction(1, W1, b1, W2, b2, W3, b3)
test_prediction(2, W1, b1, W2, b2, W3, b3)  
test_prediction(3, W1, b1, W2, b2, W3, b3)

# running model on test set
dev_predictions = make_predictions(X_dev, W1, b1, W2, b2, W3, b3)
print(get_accuracy(dev_predictions, Y_dev))