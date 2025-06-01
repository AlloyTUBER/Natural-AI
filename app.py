import streamlit as st
import joblib
import pandas as pd
import re

model = joblib.load('sentiment_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    return text.strip()

def predict_sentiment(text):
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])
    prediction = model.predict(X)[0]
    return prediction

st.set_page_config(page_title="App Review Sentiment + Recommender", layout="centered")
st.title("📱 App Review Sentiment Classifier + Recommender")

st.write("Enter a review to predict its sentiment and get app/game recommendations.")

user_input = st.text_area("Enter your review here:")

if st.button("Analyze & Recommend"):
    if user_input.strip():
        sentiment = predict_sentiment(user_input)
        st.success(f"Predicted Sentiment: **{sentiment.upper()}**")

        if sentiment == 'positive':
            # Load data
            apps_info = pd.read_csv("apps_info.csv")
            games_info = pd.read_csv("games_info.csv")
            reviews_df = pd.read_csv("apps_reviews.csv")
            games_reviews = pd.read_csv("games_reviews.csv")
            games_reviews = games_reviews.rename(columns={'game_id': 'app_id'})
            reviews_df = pd.concat([reviews_df, games_reviews], ignore_index=True)
            reviews_df.dropna(subset=['review_text', 'review_score'], inplace=True)

            reviews_df['sentiment'] = reviews_df['review_score'].apply(
                lambda x: 'positive' if x >= 4 else 'neutral' if x == 3 else 'negative'
            )

            positive_reviews = reviews_df[reviews_df['sentiment'] == 'positive']
            top_apps = positive_reviews['app_id'].value_counts().head(5).index.tolist()

            recommended_apps = apps_info[apps_info['app_id'].isin(top_apps)][['app_name', 'score', 'categories']]
            games_info = games_info.rename(columns={'game_id': 'app_id'})
            recommended_games = games_info[games_info['app_id'].isin(top_apps)][['game_name', 'score', 'categories']]

            st.markdown("### 📲 Recommended Apps:")
            st.dataframe(recommended_apps)

            st.markdown("### 🎮 Recommended Games:")
            st.dataframe(recommended_games)
        else:
            st.info("Recommendations are only shown for positive reviews.")
    else:
        st.warning("Please enter a review first.")
