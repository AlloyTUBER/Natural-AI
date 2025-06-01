import streamlit as st
import tensorflow as tf
from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image

# Load pre-trained MobileNet model
model = MobileNet(weights='imagenet')

st.set_page_config(page_title="Image Classifier with MobileNet")
st.title("🧠 Image Classifier (MobileNet)")
st.write("Upload an image and I'll tell you what it is!")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption='Uploaded Image', use_column_width=True)

    # Preprocess image for MobileNet
    img_resized = img.resize((224, 224))
    img_array = image.img_to_array(img_resized)
    img_batch = np.expand_dims(img_array, axis=0)
    img_preprocessed = preprocess_input(img_batch)

    # Predict
    preds = model.predict(img_preprocessed)
    top_preds = decode_predictions(preds, top=3)[0]

    st.subheader("🔍 Top Predictions:")
    for i, (imagenet_id, label, prob) in enumerate(top_preds):
        st.write(f"**{i+1}. {label.capitalize()}** — {prob*100:.2f}%")

    # Optional: bar chart
    import pandas as pd
    df = pd.DataFrame({
        'Label': [label.capitalize() for (_, label, _) in top_preds],
        'Probability': [prob for (_, _, prob) in top_preds]
    }).set_index('Label')
    st.bar_chart(df)
