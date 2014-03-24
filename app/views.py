from datetime import datetime

import facebook
from flask import jsonify, make_response, redirect, render_template, request, \
                  url_for
from requests import get

from app import api, app, auth, db
from config import FACEBOOK_APP_ID, FACEBOOK_APP_NAME, LONG_TERM_TOKEN, \
                   SHORT_TERM_TOKEN, API_USERNAME, API_PASSWORD, API_VERSION
from forms import AdvancedMoodForm, BasicMoodForm, ConsentForm
from models import Mood, MoodAPI, MoodListAPI, Token, TokenAPI, TokenListAPI, \
                   User, UserAPI, UserListAPI, UserMoodListAPI, \
                   UserTokenListAPI
from utils import channel, get_current_user

@auth.get_password
def get_password(username):
    if username == API_USERNAME:
        return API_PASSWORD
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

    if not user:
        return render_template('login.html', app_id=FACEBOOK_APP_ID,
                               channel_url=channel(), name=FACEBOOK_APP_NAME,
                               year=year)

    if user.consented:
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
            return render_template('login.html', app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(),
                                   name=FACEBOOK_APP_NAME, year=year)
    else:
        graph = facebook.GraphAPI(user.get_short_term_token().access_token)
        profile = graph.get_object('me')

        return render_template('consent.html', consent_form=ConsentForm(),
                               me=profile, user=user)


@app.route('/consent/', methods=['POST'])
def post_consent():
    current_user = get_current_user()

    if current_user:
        short_term_token = current_user.get_short_term_token().access_token

        graph = facebook.GraphAPI(short_term_token)
        profile = graph.get_object('me')

        # Decide what form we want to show the user
        if not current_user.consented:
            form = ConsentForm()

            if form.validate_on_submit():
                # TODO (Mitch): validate that each checkbox is true
                current_user.consented = True
                db.session.commit()

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

"""
Custom error pages
"""
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', year=datetime.utcnow().year), 500

"""
API Resouces
"""
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
