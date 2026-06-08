import numpy as np
import os
import tensorflow as tf
from tensorflow.keras import layers, models

data_path = "data"

X = []
y = []
classes = []

samples_per_class = 3000

print("Loading datasets...")

for i, file in enumerate(sorted(os.listdir(data_path))):
    if file.endswith(".npy"):
        label = file.replace(".npy", "")
        classes.append(label)

        print(f"Loading {label}...")

        data = np.load(os.path.join(data_path, file))
        data = data[:samples_per_class]

        X.append(data)
        y.extend([i] * len(data))

X = np.concatenate(X)
y = np.array(y)

# Normalize
X = X / 255.0
X = X.reshape(-1, 28, 28, 1)

# Shuffle
indices = np.arange(len(X))
np.random.shuffle(indices)
X = X[indices]
y = y[indices]

# Split
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

print("Building model...")

model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(28,28,1)),
    layers.BatchNormalization(),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(128, (3,3), activation='relu'),
    layers.Flatten(),

    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),

    layers.Dense(len(classes), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("Training...")

model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=64,
    validation_data=(X_test, y_test)
)

# Save model
model.save("final_model.keras")
np.save("labels.npy", classes)

print("✅ Training complete!")