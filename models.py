from flask_sqlalchemy import SQLAlchemy

# Creates DB objects from SQLAlchemy class
DB = SQLAlchemy()


# Make a User table with SQLAlchemy
class User(DB.Model):
    id = DB.Column(DB.BigInteger, primary_key=True)
    username = DB.Column(DB.String, nullable=False)
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return f"<User: {self.username}>"


# Make a Tweet table with SQLAlchemy
class Tweet(DB.Model):
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(300))
    vector = DB.Column(DB.PickleType, nullable=True)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return f"<Tweet: {self.text}>"
