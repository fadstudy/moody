
from datetime import datetime

import facebook
from flask import redirect, render_template, request, url_for

from app import app, db
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
        query = db.session.query(User).filter(User.facebook_id == token['uid'])
        user = query.first()

        if not user:
            user = User(facebook_id=token['uid'],
                        short_term_access_token=token['access_token'])
            db.session.add(user)
        else:
            # TODO: Remove the role
            db.session.query(User).filter(User.facebook_id == token['uid']).\
                                   update({"short_term_access_token": \
                                           token['access_token'], "role": 1,
                                           "last_visit": datetime.utcnow()})

        db.session.commit()
    except:
        query = db.session.query(User).filter(User.facebook_id == token)
        user = query.first()

    return user

def is_user_admin(user):
    return True if user.role == 1 else False

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')

@app.route('/')
def index():
    user = get_user()

    if user:
        try:
            graph = facebook.GraphAPI(user.short_term_access_token)
            profile = graph.get_object("me")

            return render_template('index.html',
                                   access_token=user.short_term_access_token,
                                   app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(),
                                   me=profile, name=FACEBOOK_APP_NAME,
                                   user=user)
        except facebook.GraphAPIError:
            pass

    return render_template('login.html', app_id=FACEBOOK_APP_ID,
                           channel_url=channel(), name=FACEBOOK_APP_NAME)

@app.route('/admin/', methods=['GET'])
def admin():
    current_user = get_user()

    if current_user and is_user_admin(current_user):
        try:
            graph = facebook.GraphAPI(current_user.short_term_access_token)
            profile = graph.get_object("me")

            query = db.session.query(User)
            users = query.all()

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

            query = db.session.query(User).filter(User.facebook_id == user_id)
            user = query.first()

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
def post_mood():
    current_user = get_user()

    if current_user:
        try:
            graph = facebook.GraphAPI(current_user.short_term_access_token)
            profile = graph.get_object("me")

            for key, value in request.form.items():
                if key == 'submit-button': continue
                if not request.form[key].isdigit():
                    return redirect('/')
            try:
                mood = request.form['mood-radio']
                user_id = request.form['user-id']

                if user_id != current_user.facebook_id:
                    return redirect('/')

                query = db.session.query(User).filter(User.facebook_id == \
                                                      user_id)
                current_user = query.first()
                current_user.moods.append(Mood(rating=mood))

                db.session.commit()
            except:
                pass

            return render_template('index.html',
                                   access_token=\
                                           current_user.short_term_access_token,
                                   app_id=FACEBOOK_APP_ID,
                                   channel_url=channel(),
                                   me=profile, name=FACEBOOK_APP_NAME,
                                   user=current_user)
        except facebook.GraphAPIError:
            pass

    return render_template('login.html', app_id=FACEBOOK_APP_ID,
                           channel_url=channel(), name=FACEBOOK_APP_NAME)
