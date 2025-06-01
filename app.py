import streamlit as st
import pandas as pd

st.set_page_config(page_title="App/Game Recommender", layout="centered")
st.title("🎮 App & Game Recommender Based on Positive Sentiment")

@st.cache_data
def load_data():
    apps_info = pd.read_csv("apps_info.csv")
    games_info = pd.read_csv("games_info.csv")
    apps_reviews = pd.read_csv("apps_reviews.csv")
    games_reviews = pd.read_csv("games_reviews.csv")

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

    return apps_info, games_info, reviews_df

apps_info, games_info, reviews_df = load_data()

keyword = st.text_input("🔍 Enter a keyword or category (e.g. fitness, racing, music):").lower().strip()

if st.button("Get Recommendations"):
    if keyword:
        apps_info['combined'] = apps_info['description'].fillna('') + ' ' + apps_info['categories'].fillna('')
        games_info['combined'] = games_info['description'].fillna('') + ' ' + games_info['categories'].fillna('')

        filtered_apps = apps_info[apps_info['combined'].str.lower().str.contains(keyword)]
        filtered_games = games_info[games_info['combined'].str.lower().str.contains(keyword)]

        def get_top_positive(df, reviews, name_col):
            merged = pd.merge(reviews, df[['app_id', name_col]], on='app_id')
            positive_counts = merged[merged['sentiment'] == 'positive']['app_id'].value_counts()
            top_ids = positive_counts.head(5).index.tolist()
            return df[df['app_id'].isin(top_ids)][[name_col, 'score', 'categories']]

        st.markdown(f"### 🎯 Results for keyword: `{keyword}`")

        if not filtered_apps.empty:
            top_apps = get_top_positive(filtered_apps, reviews_df, 'app_name')
            st.markdown("#### 📱 Top Positively Reviewed Apps:")
            st.dataframe(top_apps)
        else:
            st.warning("No apps found matching that keyword.")

        if not filtered_games.empty:
            top_games = get_top_positive(filtered_games, reviews_df, 'game_name')
            st.markdown("#### 🎮 Top Positively Reviewed Games:")
            st.dataframe(top_games)
        else:
            st.warning("No games found matching that keyword.")
    else:
        st.warning("Please enter a keyword to get recommendations.")
