import os 
from flask import Flask, render_template, request
from twitoff.predict import predict_user
from .twitter import add_or_update_user, vectorize_tweets
from .models import DB, User, Tweet


def create_app():
    app = Flask(__name__)
    app_title = "TwitOff DS38"

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route("/test")
    def test():
        return f"<p>This is a page for {app_title}</p>"
    
    @app.route("/reset")
    def reset():
        DB.drop_all()
        DB.create_all()
        return """
        The database has been reset
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate'>Go to populate</a>
        """
    
    @app.route('/populate')
    def populate():
        user1 = User(id=1, username='jon')
        DB.session.add(user1)
        user2 = User(id=2, username='alyssa')
        DB.session.add(user2)
        tweet_text = 'This is my tweet'
        tweet_vector = vectorize_tweets(tweet_text)
        tweet1 = Tweet(id=1, text=tweet_text, vector=tweet_vector, user=user1)
        tweet_text = 'Hello World'
        tweet_vector = vectorize_tweets(tweet_text)
        tweet2 = Tweet(id=2, text=tweet_text, vector=tweet_vector, user=user2)
        DB.session.add(tweet2)
        DB.session.commit()

        return """
        The database has been reset
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate'>Go to populate</a>
        """

    @app.route('/update')
    def update():
        usernames = []
        for user in User.query.all():
            add_or_update_user(user.username)
    
    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):
        username = username or request.values['username']
        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'User {username} successfully added!'
            tweets = User.query.filter(
                User.username == username
            ).one().tweets
        except Exception as e:
            message = f'Error adding {username}: {e}'
            tweets = []

        return render_template(
            'user.html',
            title=username,
            message=message,
            tweets=tweets,
        )
    
    @app.route('/compare', methods=['POST'])
    def compare():
        username0 = request.values['user0']
        username1 = request.values['user1']

        if username0 == username1:
            message = 'Cannot compare users to themselves'
        else:
            hypo_tweet_text = request.values['tweet_text']
            prediction = predict_user(username0, username1, hypo_tweet_text)
            if prediction:
                selected_user = username1
            else:
                selected_user = username0
            message = f" '{hypo_tweet_text}' is more likely said by {selected_user}"
        
        return render_template('prediction.html', title='Prediction', message=message)

    return app