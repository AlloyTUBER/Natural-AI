import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

apps_reviews = pd.read_csv('apps_reviews.csv')
games_reviews = pd.read_csv('games_reviews.csv')
apps_info = pd.read_csv('apps_info.csv')
games_info = pd.read_csv('games_info.csv')

games_reviews = games_reviews.rename(columns={'game_id': 'app_id'})
games_info = games_info.rename(columns={'game_id': 'app_id'})

reviews_df = pd.concat([apps_reviews, games_reviews], ignore_index=True)
reviews_df.dropna(subset=['review_text', 'review_score'], inplace=True)

def label_sentiment(score):
    if score >= 4:
        return 'positive'
    elif score == 3:
        return 'neutral'
    else:
        return 'negative'

reviews_df['sentiment'] = reviews_df['review_score'].apply(label_sentiment)

import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    return text.strip()

reviews_df['clean_text'] = reviews_df['review_text'].apply(clean_text)

def predict_sentiment(texts, vectorizer, model):
    cleaned_texts = [clean_text(t) for t in texts]
    X_new = vectorizer.transform(cleaned_texts)
    predictions = model.predict(X_new)
    return predictions

vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
X = vectorizer.fit_transform(reviews_df['clean_text'])
y = reviews_df['sentiment']

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))

sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d',
            xticklabels=model.classes_, yticklabels=model.classes_)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Sentiment Confusion Matrix')
plt.show()

def recommend_apps_and_games(reviews_df, apps_info, games_info, top_n=5):
    positive_reviews = reviews_df[reviews_df['sentiment'] == 'positive']
    top_apps = positive_reviews['app_id'].value_counts().head(top_n).index.tolist()
    recommended_apps = apps_info[apps_info['app_id'].isin(top_apps)][['app_name', 'score', 'categories']]
    if 'game_name' in games_info.columns:
        recommended_games = games_info[games_info['app_id'].isin(top_apps)][['game_name', 'score', 'categories']]
    else:
        recommended_games = games_info[games_info['app_id'].isin(top_apps)][['app_id', 'score', 'categories']]
    print("\nRecommended Apps Based on Positive Sentiment:")
    print(recommended_apps)
    if not recommended_games.empty:
        print("\nRecommended Games Based on Positive Sentiment:")
        print(recommended_games)



