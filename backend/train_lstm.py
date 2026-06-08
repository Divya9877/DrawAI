import numpy as np
import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.sequence import pad_sequences

data_path = "stroke_data"  # folder where stroke JSON will be stored

X = []
y = []
labels = []

print("Loading stroke data...")

# 🔥 Load stroke files
for i, file in enumerate(os.listdir(data_path)):
    if file.endswith(".npy"):
        label = file.replace(".npy", "")
        labels.append(label)

        data = np.load(os.path.join(data_path, file), allow_pickle=True)

        for stroke in data:
            sequence = []

            for point in stroke:
                x, y, t = point
                sequence.append([x, y, t])

            X.append(sequence)
            y.append(i)

# 🔥 Pad sequences (important)
X = pad_sequences(X, padding='post', dtype='float32')

y = np.array(y)

print("Building LSTM model...")

model = models.Sequential([
    layers.Masking(mask_value=0.0, input_shape=(X.shape[1], 3)),

    layers.LSTM(128, return_sequences=True),
    layers.LSTM(64),

    layers.Dense(64, activation='relu'),
    layers.Dense(len(labels), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("Training...")

model.fit(X, y, epochs=10, batch_size=32)

# Save
model.save("lstm_model.keras")
np.save("lstm_labels.npy", labels)

print("✅ LSTM model trained!")