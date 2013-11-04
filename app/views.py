
from datetime import datetime

import facebook
from flask import redirect, render_template, request, url_for

from app import app, db
from forms import BasicMoodForm, AdvancedMoodForm
from models import User, Mood

# TODO: Hook these up via the config
FACEBOOK_APP_ID = '498777246878058'
FACEBOOK_APP_NAME = 'The FAD Study'
FACEBOOK_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'

# TODO: Maybe think about moving these to another file.
def channel():
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    return channel_url

def get_user():
    token = facebook.get_user_from_cookie(request.cookies, FACEBOOK_APP_ID,
                                          FACEBOOK_APP_SECRET)

    try:
        user = User.query.filter(User.facebook_id == token['uid']).first()

        if not user:
            user = User(facebook_id=token['uid'],
                        short_term_access_token=token['access_token'])
            db.session.add(user)
        else:
            User.query.filter(User.facebook_id == token['uid']).\
                              update({"short_term_access_token": \
                                      token['access_token'],
                                      "last_visit": datetime.utcnow()})

        db.session.commit()
    except:
        user = User.query.filter(User.facebook_id == token).first()

    return user

def is_user_admin(user):
    return True if user.role == 1 else False

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')

@app.route('/')
def index():
    try:
        user = get_user()

        if user:
            try:
                graph = facebook.GraphAPI(user.short_term_access_token)
                profile = graph.get_object("me")

                # Decide what form we want to show the user
                if user.has_answered_advanced_questions_recently():
                    form = BasicMoodForm()
                else:
                    form = AdvancedMoodForm()

                return render_template('index.html',
                                       access_token=user.short_term_access_token,
                                       app_id=FACEBOOK_APP_ID,
                                       channel_url=channel(), form=form,
                                       me=profile, name=FACEBOOK_APP_NAME,
                                       user=user)
            except facebook.GraphAPIError:
                pass

        return render_template('login.html', app_id=FACEBOOK_APP_ID,
                               channel_url=channel(), name=FACEBOOK_APP_NAME)
    except Exception as e:
        return 'Error: {0}'.format(e)

@app.route('/admin/', methods=['GET'])
def admin():
    current_user = get_user()

    if current_user and is_user_admin(current_user):
        try:
            graph = facebook.GraphAPI(current_user.short_term_access_token)
            profile = graph.get_object("me")

            users = User.query.all()

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

@app.route('/users/<int:user_id>/')
@app.route('/users/<int:user_id>')
def user(user_id):
    current_user = get_user()

    if current_user and is_user_admin(current_user):
        try:
            graph = facebook.GraphAPI(current_user.short_term_access_token)
            profile = graph.get_object("me")

            user = User.query.filter(User.facebook_id == str(user_id)).first()

            # TODO: rename chungus
            return render_template('users.html', app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(), me=profile,
                                   name=FACEBOOK_APP_NAME, user=current_user,
                                   chungus=user)
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
        try:
            graph = facebook.GraphAPI(current_user.short_term_access_token)
            profile = graph.get_object("me")

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

            return render_template('index.html',
                                   access_token=\
                                           current_user.short_term_access_token,
                                   app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(), form=form,
                                   me=profile, name=FACEBOOK_APP_NAME,
                                   user=current_user)
        except facebook.GraphAPIError:
            pass

    return render_template('login.html', app_id=FACEBOOK_APP_ID,
                           channel_url=channel(), name=FACEBOOK_APP_NAME)
