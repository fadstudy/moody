from datetime import datetime

import facebook
from flask import jsonify, make_response, redirect, render_template, request, \
                  url_for
from requests import get

from app import api, app, auth, db
from forms import AdvancedMoodForm, BasicMoodForm
from models import Mood, MoodAPI, MoodListAPI, Token, TokenAPI, TokenListAPI, \
                   User, UserAPI, UserListAPI, UserMoodListAPI, UserTokenListAPI

import config
from utils import channel, get_current_user

# TODO: Hook these up via the config
FACEBOOK_APP_ID = '498777246878058'
FACEBOOK_APP_NAME = 'The FAD Study'
FACEBOOK_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'
API_VERSION = 'v0.3'

SHORT_TOKEN = 0
LONG_TOKEN = 1

issue_robot_username = 'fadstudyrobot'
issue_robot_password = 'fad$tudyr0b0t'

# TODO: Maybe think about moving these to another file.
@auth.get_password
def get_password(username):
    if username == 'apiuser':
        return 'letmeinbrah!'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'message': 'Unauthorized access' } ), 403)

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    user = get_current_user()

    date = datetime.now().strftime('%A, %B %d')
    year = datetime.utcnow().year

    if user:
        try:
            graph = facebook.GraphAPI(user.get_short_term_token().access_token)
            profile = graph.get_object('me')

            # Decide what form we want to show the user
            if user.has_answered_advanced_questions_recently():
                mood_form = BasicMoodForm()
            else:
                mood_form = AdvancedMoodForm()

            return render_template('index.html',
                                   access_token=user.get_short_term_token() \
                                                    .access_token,
                                   app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(), date=date,
                                   mood_form=mood_form,
                                   me=profile, name=FACEBOOK_APP_NAME,
                                   user=user, year=year)
        except facebook.GraphAPIError:
            pass

    return render_template('login.html', app_id=FACEBOOK_APP_ID,
                           channel_url=channel(), name=FACEBOOK_APP_NAME,
                           year=year)

@app.route('/admin/')
def admin():
    current_user = get_current_user()

    if current_user and current_user.is_admin():
        try:
            graph = facebook.GraphAPI(current_user.get_short_term_token() \
                                      .access_token)
            profile = graph.get_object('me')

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
    current_user = get_current_user()

    if current_user and current_user.is_admin:
        try:
            graph = facebook.GraphAPI(current_user.get_short_term_token() \
                                      .access_token)
            profile = graph.get_object('me')

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
    current_user = get_current_user()

    if current_user and current_user.is_admin():
        try:
            graph = facebook.GraphAPI(current_user.get_short_term_token() \
                                      .access_token)
            profile = graph.get_object('me')

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
    current_user = get_current_user()

    if current_user:
        short_term_token = current_user.get_short_term_token().access_token

        try:
            graph = facebook.GraphAPI(short_term_token)
            profile = graph.get_object('me')

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
    current_user = get_current_user()

    if current_user and current_user.is_admin():
        try:
            User.query.filter(User.facebook_id == str(user_id)).\
                             update({ 'role': request.args.get('role') })
            db.session.commit()
            return '', 200
        except Exception as e:
            return '{0}'.format(e), 500
    return '', 404

api.add_resource(UserListAPI, '/api/{0}/users'.format(API_VERSION),
                 endpoint='Users')
api.add_resource(UserAPI, '/api/{0}/users/<int:id>'.format(API_VERSION),
                 endpoint='User')
api.add_resource(UserMoodListAPI, '/api/{0}/users/<int:id>/moods'
                 .format(API_VERSION), endpoint='UserMoods')
api.add_resource(MoodListAPI, '/api/{0}/moods'.format(API_VERSION),
                 endpoint='Moods')
api.add_resource(MoodAPI, '/api/{0}/moods/<int:id>'.format(API_VERSION),
                 endpoint='Mood')
api.add_resource(UserTokenListAPI, '/api/{0}/users/<int:id>/tokens'
                 .format(API_VERSION), endpoint='UserTokens')
api.add_resource(TokenListAPI, '/api/{0}/tokens'.format(API_VERSION),
                 endpoint='Tokens')
api.add_resource(TokenAPI, '/api/{0}/tokens/<int:id>'.format(API_VERSION),
                 endpoint='Token')
