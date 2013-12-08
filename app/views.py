from datetime import datetime

import facebook
from flask import jsonify, make_response, redirect, render_template, request, \
                  url_for
from requests import get

from app import api, app, auth, db
from forms import AdvancedMoodForm, BasicMoodForm
from models import Mood, MoodAPI, MoodListAPI, Token, TokenAPI, TokenListAPI, \
                   User, UserAPI, UserListAPI, UserMoodListAPI, UserTokenListAPI

# TODO: Hook these up via the config
FACEBOOK_APP_ID = '498777246878058'
FACEBOOK_APP_NAME = 'The FAD Study'
FACEBOOK_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'

SHORT_TOKEN = 0
LONG_TOKEN = 1

# TODO: Maybe think about moving these to another file.
@auth.get_password
def get_password(username):
    if username == 'apiuser':
        return 'letmeinbrah!'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'message': 'Unauthorized access' } ), 403)

def channel():
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    return channel_url

def get_short_term_token(user):
    return [i for i in user.tokens if i._type == SHORT_TOKEN][0].access_token

def exchange_token(short_term_token):
    payload = { 'grant_type': 'fb_exchange_token',
                'client_id': FACEBOOK_APP_ID,
                'client_secret': FACEBOOK_APP_SECRET,
                'fb_exchange_token': short_term_token }

    result = get('https://graph.facebook.com/oauth/access_token',
                 params=payload).content

    return result.split('=')[1].split('&')[0]

def get_user():
    token = facebook.get_user_from_cookie(request.cookies, FACEBOOK_APP_ID,
                                          FACEBOOK_APP_SECRET)

    try:
        user = User.query.filter(User.facebook_id == token['uid']).first()

        # If the user doesn't exist, add them to the database.
        if not user:
            user = User(facebook_id=token['uid'])
            db.session.add(user)

            # Add the new user's short and long term tokens to the DB.
            user.tokens.append(Token(token['access_token'], SHORT_TOKEN))
            user.tokens.append(Token(exchange_token(token['access_token']),
                                     LONG_TOKEN))
        else:
            # This is only to handle legacy database users on the heroku
            # platform
            if len(user.tokens) == 0:
                user.tokens.append(Token(token['access_token'], SHORT_TOKEN))
                user.tokens.append(Token(exchange_token(token['access_token']),
                                         LONG_TOKEN))

            # Update the user's short term access token
            Token.query.filter(Token.user_id == user.id
                               and Token._type == SHORT_TOKEN) \
                              .update({ 'access_token': token['access_token'],
                                        'created_date': datetime.utcnow(),
                                        'expiry_date': datetime.utcnow() })

            # Check and exchange for a long term access token
            if user.needs_to_exchange_for_long_term_token():
                print 'Exchanging for long token'
                long_term_token = Token(exchange_token(get_short_term_token(user
                                                      )), LONG_TOKEN)
                user.tokens.append(long_term_token)

            # Update the user's last_visit property
            User.query.filter(User.facebook_id == token['uid']) \
                             .update({ "last_visit": datetime.utcnow() })
    except:
        user = User.query.filter(User.facebook_id == token).first()
        User.query.filter(User.facebook_id == token) \
                         .update({ "last_visit": datetime.utcnow() })

    db.session.commit()
    return user

def is_user_admin(user):
    return True if user.role == 1 else False

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    user = get_user()

    if user:
        try:
            short_term_token = get_short_term_token(user)

            graph = facebook.GraphAPI(short_term_token)
            profile = graph.get_object("me")

            # Decide what form we want to show the user
            if user.has_answered_advanced_questions_recently():
                mood_form = BasicMoodForm()
            else:
                mood_form = AdvancedMoodForm()

            return render_template('index.html',
                                   access_token=short_term_token,
                                   app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(),
                                   mood_form=mood_form,
                                   me=profile, name=FACEBOOK_APP_NAME,
                                   user=user)
        except facebook.GraphAPIError:
            pass

    return render_template('login.html', app_id=FACEBOOK_APP_ID,
                           channel_url=channel(), name=FACEBOOK_APP_NAME)

@app.route('/admin/')
def admin():
    current_user = get_user()

    if current_user and is_user_admin(current_user):
        try:
            graph = facebook.GraphAPI(get_short_term_token(current_user))
            profile = graph.get_object("me")

            users = User.query.all()[:5]

            return render_template('admin.html', app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(), me=profile,
                                   name=FACEBOOK_APP_NAME, user=current_user,
                                   users=users)
        except facebook.GraphAPIError:
            pass
    elif not current_user:
        return render_template('login.html', app_id=FACEBOOK_APP_ID,
                               channel_url=channel(), name=FACEBOOK_APP_NAME)
    else:
        return redirect('/')

@app.route('/admin/users/')
def users():
    current_user = get_user()

    if current_user and is_user_admin(current_user):
        try:
            graph = facebook.GraphAPI(get_short_term_token(current_user))
            profile = graph.get_object("me")

            users = User.query.all()

            return render_template('users.html', app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(), me=profile,
                                   name=FACEBOOK_APP_NAME, user=current_user,
                                   users=users)
        except facebook.GraphAPIError:
            pass
    elif not current_user:
        return render_template('login.html', app_id=FACEBOOK_APP_ID,
                               channel_url=channel(), name=FACEBOOK_APP_NAME)
    else:
        return redirect('/')

@app.route('/admin/users/<int:user_id>/')
@app.route('/admin/users/<int:user_id>')
def user(user_id):
    current_user = get_user()

    if current_user and is_user_admin(current_user):
        try:
            graph = facebook.GraphAPI(get_short_term_token(current_user))
            profile = graph.get_object("me")

            user = User.query.filter(User.facebook_id == str(user_id)).first()

            # TODO: rename chungus
            return render_template('user.html', app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(), me=profile,
                                   name=FACEBOOK_APP_NAME, user=user,
                                   chungus=current_user)
        except facebook.GraphAPIError:
            pass
    elif not current_user:
        return render_template('login.html', app_id=FACEBOOK_APP_ID,
                               channel_url=channel(), name=FACEBOOK_APP_NAME)
    else:
        return redirect('/')

@app.route('/moods/new', methods=['POST'])
@app.route('/moods/new/', methods=['POST'])
def post_mood():
    current_user = get_user()

    if current_user:
        short_term_token = get_short_term_token(current_user)

        try:
            graph = facebook.GraphAPI(short_term_token)
            profile = graph.get_object("me")

            # Decide what form we want to show the user
            if current_user.has_answered_advanced_questions_recently():
                form = BasicMoodForm()

                if form.validate_on_submit():
                    mood_rating = form.moods.data

                    mood = Mood(rating=mood_rating)

                    current_user.moods.append(mood)
                    db.session.commit()

                    return redirect('/')
                else:
                    return render_template('index.html',
                                           access_token=short_term_token,
                                           app_id=FACEBOOK_APP_ID,
                                           channel_url=channel(), form=form,
                                           me=profile, name=FACEBOOK_APP_NAME,
                                           user=current_user)

            else:
                form = AdvancedMoodForm()

                if form.validate_on_submit():
                    mood_rating = form.moods.data
                    hospital = form.hospital.data
                    hospital_reason = form.hospital_reason.data
                    medication = form.medication.data
                    medication_reason = form.medication_reason.data

                    mood = Mood(rating=mood_rating, hospital=hospital,
                                hospital_bipolar_related=hospital_reason,
                                medication=medication,
                                medication_bipolar_related=medication_reason)

                    current_user.moods.append(mood)
                    db.session.commit()

                    return redirect('/')
                else:
                    return render_template('index.html',
                                           access_token=short_term_token,
                                           app_id=FACEBOOK_APP_ID,
                                           channel_url=channel(), form=form,
                                           me=profile, name=FACEBOOK_APP_NAME,
                                           user=current_user)
        except facebook.GraphAPIError:
            pass

    return render_template('login.html', app_id=FACEBOOK_APP_ID,
                           channel_url=channel(), name=FACEBOOK_APP_NAME)

# TODO: Fix this method up to be a PUT request where we pass the user object
# with the updated role to the method.  From there we just update the method.
# The URI will be PUT: /users/:user/
@app.route('/make_admin/<int:user_id>')
def promote_to_admin(user_id):
    current_user = get_user()

    if current_user and is_user_admin(current_user):
        try:
            User.query.filter(User.facebook_id == str(user_id)).\
                             update({"role": request.args.get('role')})
            db.session.commit()
            return '', 200
        except Exception as e:
            return '{0}'.format(e), 500
    return '', 404

# TODO: Hook up version in config
api.add_resource(UserListAPI, '/api/v0.3/users', endpoint='Users')
api.add_resource(UserAPI, '/api/v0.3/users/<int:id>', endpoint='User')
api.add_resource(UserMoodListAPI, '/api/v0.3/users/<int:id>/moods',
                 endpoint='UserMoods')
api.add_resource(MoodListAPI, '/api/v0.3/moods', endpoint='Moods')
api.add_resource(MoodAPI, '/api/v0.3/moods/<int:id>', endpoint='Mood')
api.add_resource(UserTokenListAPI, '/api/v0.3/users/<int:id>/tokens',
                 endpoint='UserTokens')
api.add_resource(TokenListAPI, '/api/v0.3/tokens', endpoint='Tokens')
api.add_resource(TokenAPI, '/api/v0.3/tokens/<int:id>', endpoint='Token')
