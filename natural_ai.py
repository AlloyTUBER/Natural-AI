import pandas as pd

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

keyword = input("Enter a keyword or category of app/game you're interested in (e.g. music, racing, education): ").lower()

apps_info['combined'] = apps_info['description'].fillna('') + ' ' + apps_info['categories'].fillna('')
games_info['combined'] = games_info['description'].fillna('') + ' ' + games_info['categories'].fillna('')

filtered_apps = apps_info[apps_info['combined'].str.lower().str.contains(keyword)]
filtered_games = games_info[games_info['combined'].str.lower().str.contains(keyword)]

def get_top_positive(df, reviews, name_col):
    merged = pd.merge(reviews, df[['app_id', name_col]], on='app_id')
    positive_counts = merged[merged['sentiment'] == 'positive']['app_id'].value_counts()
    top_ids = positive_counts.head(5).index.tolist()
    return df[df['app_id'].isin(top_ids)][[name_col, 'score', 'categories']]

print(f"\n🎯 Results for keyword: '{keyword}'")

if not filtered_apps.empty:
    top_apps = get_top_positive(filtered_apps, reviews_df, 'app_name')
    print("\n📱 Top Positively Reviewed Apps:")
    print(top_apps.to_string(index=False))
else:
    print("\n📱 No apps found matching that keyword.")

if not filtered_games.empty:
    top_games = get_top_positive(filtered_games, reviews_df, 'game_name')
    print("\n🎮 Top Positively Reviewed Games:")
    print(top_games.to_string(index=False))
else:
    print("\n🎮 No games found matching that keyword.")
