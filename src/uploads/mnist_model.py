import tensorflow as tf  ## main library for deep learning , building and training neural network
from tensorflow.keras.datasets import mnist ##built-in dataset of handwritten digits 0-9
from tensorflow.keras.models import Sequential ## a simple way to stack layers one after another in a model
from tensorflow.keras.layers import Dense, Flatten ## types of layers: Dense=fully connected, flatten= reshapes data
from tensorflow.keras.utils import to_categorical ## converts labels 0-9 into one-hot vectors , ex:1-> [0,1,0]
import matplotlib.pyplot as plt ## for plotting (displaying) images
import numpy as np ## for numerical operations

## load data from the data set , x : image y: label
(x_train, y_train), (x_test, y_test) = mnist.load_data()

##normalize, make the numbers smaller so the neural network learns it faster and more accurate
x_train = x_train / 255.0
x_test = x_test / 255.0

##to_categorical() convert numbers into one-hot victors , ex: 7 -> [0,0,0,0,0,0,0,1,0,0]
##y_train = to_categorical(y_train)
##y_test = to_categorical(y_test)


## Build the model in keras , the layers are stacked one after another
## you feed input at the first layer , it goes through each layer in order
model = Sequential([
    ## MNIST image's are 2D array , Flatten converts it into 1D vector of (28*28 numbers)
    ##this is needed because denes layers only except 1D input
    Flatten(input_shape=(28,28)),
    ## try to find pattern , learn meaningful features of the image
    Dense(128, activation='relu'),
    ## final decision layer , 10 neurons because there are 10 possible digits
    ## Softmax turns the numbers of each neuron outputs into probabilities that sum to 1
    Dense(10, activation='softmax')
])

## categorical_crossentropy expect one-hot , other loss func: sparse_categorical_crossentropy : except integer labels
model.compile(optimizer='adam', ## tells the model how to adjust to the weights to learn from data , Adam is a popular optimizer fast, works well
              loss='sparse_categorical_crossentropy', ##this measures how wrong the model is compared to the true table , Lower loss = model is predicting better
              metrics=['accuracy']) ## tells keras to track accuracy while training o see how often the model is right

##train the model , epochs=how many times the network sees the full training set , batch size= number of images processed at once
## validation split = the percentage of training data used to check if the model is learning well
## Keras shuffles the training images by default every epoch → so the model doesn’t always see them in the same order.
model.fit(x_train, y_train, epochs=5, batch_size=32, validation_split=0.1)

##check how well the model performs on unseen data , test_acc= test accuracy
test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc}")

## make prediction for the test images
predictions = model.predict(x_test)
print("First image prediction:", predictions[0].argmax())

# pick 10 random test images to display
num_images = 10
indices = np.random.choice(len(x_test), num_images, replace=False)  # pick 10 random num from the test set
test_images = x_test[indices]
test_labels = y_test[indices]


# Predict the digits
predictions = model.predict(test_images)

# Plot images with predicted labels
plt.figure(figsize=(12, 4))
for i in range(num_images):
    plt.subplot(2, 5, i+1) ## create 2 rows * 5 columns of images , i+1 because pos start from 1 not 0 , i =0 -> 0+1=1
    plt.imshow(test_images[i], cmap='gray') ## show image in grayscale
    ##shows predicted digit and true table
    plt.title(f"Pred: {np.argmax(predictions[i])}\nTrue: {test_labels[i]}", fontsize=10, multialignment='center')
    plt.axis('off') ## hides axes for cleaner look.
plt.tight_layout()
plt.show()

