
"""Connects to Twitter API via tweepy"""

import os
import tweepy
import spacy
from .models import DB, Tweet, User
from tweepy.errors import TweepError

# Get API keys
key = os.getenv('TWITTER_API_KEY')
secret = os.getenv('TWITTER_API_KEY_SECRET')

# Connect to Twitter API
twitter_auth = tweepy.OAuthHandler(key, secret)
twitter = tweepy.API(twitter_auth)

# Load pretrained SpaCy World Embeddings model
nlp = spacy.load('my_model')

def vectorize_tweets(nlp, tweet_text):
    return nlp(tweet_text).vector

def add_or_update_user(twitter, nlp, session, username):
    """
    Pull a user and their tweets from the Twitter API.
    Save them in the DB.
    """
    try:
        twitter_user = twitter.get_user(screen_name=username)
        # Does this user already exist in the db?
        db_user  = session.query(User).filter(User.id==twitter_user.id).first()
        if not db_user:
            db_user = User(id=twitter_user.id, username=username)
            session.add(db_user)
        
        # Get the user's tweets
        tweets = twitter_user.timeline(
            count=200,
            exclude_replies=True,
            include_rts=False,
            tweet_mode='extended'
        )

        # Add each tweet to the db
        for tweet in tweets:
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300], vector=vectorize_tweets(nlp, tweet.full_text))
            db_user.tweets.append(db_tweet)
            session.add(db_tweet)
    except TweepError as e:
        print(f'Error processing {username}: {e}')
        raise e
    
    # Save our changes
    DB.session.commit()