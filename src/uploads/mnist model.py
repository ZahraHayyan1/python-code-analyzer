import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
import matplotlib.pyplot as plt
import numpy as np

## load data from data set
(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train = x_train / 255.0
x_test = x_test / 255.0

##build the model layers
model = Sequential([
    Flatten(input_shape=(28,28)),
    Dense(128, activation='relu'),
    Dense(10, activation='softmax')
])


model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

##train the model
model.fit(x_train, y_train, epochs=5, batch_size=32, validation_split=0.1)

test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc}")

predictions = model.predict(x_test)
print("First image prediction:", predictions[0].argmax())

##pick 10 random test images to display
num_images = 10
indices = np.random.choice(len(x_test), num_images, replace=False)
test_images = x_test[indices]
test_labels = y_test[indices]

predictions = model.predict(test_images)

plt.figure(figsize=(12, 4))
for i in range(num_images):
    plt.subplot(2, 5, i+1)
    plt.imshow(test_images[i], cmap='gray')
    plt.title(f"Pred: {np.argmax(predictions[i])}\nTrue: {test_labels[i]}", fontsize=10, multialignment='center')
    plt.axis('off')
plt.tight_layout()
plt.show()
