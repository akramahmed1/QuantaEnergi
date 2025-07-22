import tensorflow as tf
model = tf.keras.Sequential([tf.keras.layers.Dense(units=1, input_shape=[1])])
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
with open("optimized_model.tflite", "wb") as f:
    f.write(tflite_model)
