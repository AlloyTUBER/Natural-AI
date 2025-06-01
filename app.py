import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import string

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

# --- Data Loading ---
apps_reviews = pd.read_csv('apps_reviews.csv')
games_reviews = pd.read_csv('games_reviews.csv')

# Rename for consistency and combine
if 'game_id' in games_reviews.columns:
    games_reviews = games_reviews.rename(columns={'game_id': 'app_id'})
reviews_df = pd.concat([apps_reviews, games_reviews], ignore_index=True)

# Drop NA reviews and scores
reviews_df.dropna(subset=['review_text', 'review_score'], inplace=True)

# --- Sentiment Labeling ---
def label_sentiment(score):
    if score >= 4:
        return 'positive'
    elif score == 3:
        return 'neutral'
    else:
        return 'negative'

reviews_df['sentiment'] = reviews_df['review_score'].apply(label_sentiment)

# --- Text Cleaning ---
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    return text.strip()

reviews_df['clean_text'] = reviews_df['review_text'].apply(clean_text)

# --- TF-IDF + Logistic Regression ---
vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
X_tfidf = vectorizer.fit_transform(reviews_df['clean_text'])
y = reviews_df['sentiment']

X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, test_size=0.2, stratify=y, random_state=42
)

lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train, y_train)
y_pred_lr = lr_model.predict(X_test)

print("Logistic Regression Classification Report:")
print(classification_report(y_test, y_pred_lr))

sns.heatmap(
    confusion_matrix(y_test, y_pred_lr),
    annot=True, fmt='d',
    xticklabels=lr_model.classes_, yticklabels=lr_model.classes_
)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Sentiment Confusion Matrix (Logistic Regression)')
plt.show()

# --- Deep Learning Model (LSTM) ---
MAX_VOCAB = 20000
MAX_LEN = 100

tokenizer = Tokenizer(num_words=MAX_VOCAB, oov_token="<OOV>")
tokenizer.fit_on_texts(reviews_df['clean_text'])
sequences = tokenizer.texts_to_sequences(reviews_df['clean_text'])
padded_sequences = pad_sequences(sequences, maxlen=MAX_LEN, padding='post', truncating='post')

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(reviews_df['sentiment'])

X_train_dl, X_test_dl, y_train_dl, y_test_dl = train_test_split(
    padded_sequences, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

lstm_model = Sequential([
    Embedding(input_dim=MAX_VOCAB, output_dim=128, input_length=MAX_LEN),
    LSTM(64),
    Dropout(0.5),
    Dense(32, activation='relu'),
    Dense(3, activation='softmax')
])

lstm_model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)
lstm_model.summary()

history = lstm_model.fit(
    X_train_dl, y_train_dl,
    validation_data=(X_test_dl, y_test_dl),
    epochs=5,
    batch_size=512
)

# --- Evaluation ---
y_pred_probs = lstm_model.predict(X_test_dl)
y_pred_dl = np.argmax(y_pred_probs, axis=1)

print("LSTM Model Classification Report:")
print(classification_report(y_test_dl, y_pred_dl, target_names=label_encoder.classes_))

plt.plot(history.history['accuracy'], label='Train Acc')
plt.plot(history.history['val_accuracy'], label='Val Acc')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.title('Training and Validation Accuracy')
plt.show()
