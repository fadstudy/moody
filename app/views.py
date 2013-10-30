
import facebook
from flask import redirect, render_template, request, url_for

from app import app, db
from models import User

FACEBOOK_APP_ID = '498777246878058'
FACEBOOK_APP_NAME = 'The FAD Study'
FACEBOOK_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')

@app.route('/')
def index():
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

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
            # Update the latest access_token
            db.session.query(User).\
                filter(User.facebook_id == token['uid']).\
                update({"short_term_access_token": token['access_token']})

        graph = facebook.GraphAPI(token["access_token"])
        profile = graph.get_object("me")

        db.session.commit()
        return render_template('index.html', app_id=FACEBOOK_APP_ID,
                               name=FACEBOOK_APP_NAME, me=profile,
                               user=user, access_token=token["access_token"],
                               channel_url=channel_url)
    except Exception as e:
        query = db.session.query(User).filter(User.facebook_id == token)
        user = query.first()

        # If we've met the user before, they'll be in the database.
        if user:
            try:
                graph = facebook.GraphAPI(user.short_term_access_token)
                profile = graph.get_object("me")

                return render_template('index.html', app_id=FACEBOOK_APP_ID,
                                       name=FACEBOOK_APP_NAME, me=profile,
                                       user=user, access_token=user.short_term_access_token,
                                       channel_url=channel_url)
            except facebook.GraphAPIError as e:
                print 'FACEBOOK GRAPH API ERROR: ', e
                pass

        return render_template('login.html', app_id=FACEBOOK_APP_ID,
                               name=FACEBOOK_APP_NAME, channel_url=channel_url)

@app.route('/admin/', methods=['GET'])
def admin():
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    token = facebook.get_user_from_cookie(request.cookies, FACEBOOK_APP_ID,
                                          FACEBOOK_APP_SECRET)

    try:
        query = db.session.query(User).filter(User.facebook_id == token['uid'])
        user = query.first()

        if user and user.role == 1:
            # Here we have an admin
            # Update the latest access_token
            db.session.query(User).\
                filter(User.facebook_id == token['uid']).\
                update({"short_term_access_token": token['access_token']})

            graph = facebook.GraphAPI(token["access_token"])
            profile = graph.get_object("me")

            db.session.commit()

            query = db.session.query(User)
            users = query.all()

            return render_template('admin.html', name=FACEBOOK_APP_NAME,
                                   me=profile, users=users, user=user)
        else:
            return redirect('/')
    except Exception as e:
        query = db.session.query(User).filter(User.facebook_id == token)
        user = query.first()

        if user and user.role == 1:
            try:
                graph = facebook.GraphAPI(user.short_term_access_token)
                profile = graph.get_object("me")

                query = db.session.query(User)
                users = query.all()

                return render_template('admin.html', name=FACEBOOK_APP_NAME,
                                       me=profile, users=users, user=user)

            except facebook.GraphAPIError as e:
                print 'FACEBOOK GRAPH API ERROR: ', e
                pass

        return redirect('/')

@app.route('/users/<int:user_id>/')
@app.route('/users/<int:user_id>')
def user(user_id):
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    token = facebook.get_user_from_cookie(request.cookies, FACEBOOK_APP_ID,
                                           FACEBOOK_APP_SECRET)

    try:
        query = db.session.query(User).filter(User.facebook_id == token['uid'])
        user = query.first()

        if user and user.role == 1:
            # Here we have an admin
            # Update the latest access_token
            db.session.query(User).\
                filter(User.facebook_id == token['uid']).\
                update({"short_term_access_token": token['access_token']})

            graph = facebook.GraphAPI(token["access_token"])
            profile = graph.get_object("me")

            db.session.commit()

            query = db.session.query(User).filter(User.facebook_id == user_id)
            chungus = query.first()

            return render_template('users.html', chungus=chungus, user=user,
                                   me=profile)
        else:
            return redirect('/')
    except Exception as e:
        query = db.session.query(User).filter(User.facebook_id == token)
        user = query.first()

        if user and user.role == 1:
            try:
                graph = facebook.GraphAPI(user.short_term_access_token)
                profile = graph.get_object("me")

                query = db.session.query(User).filter(User.facebook_id == user_id)
                chungus = query.first()

                return render_template('users.html', chungus=chungus, user=user,
                                       me=profile)

            except facebook.GraphAPIError as e:
                print 'FACEBOOK GRAPH API ERROR: ', e
                pass

        return redirect('/')

@app.route('/moods/new', methods=['POST'])
def post_mood():
    for key, value in request.form.items():
        if key == 'submit-button': continue
        if not request.form[key].isdigit():
            pass # return 400

    # mood = Mood(request.form['mood-radio'], request.form['hospital-radio'],
    #             request.form['medication-radio'], request.form['user-id'])

    return redirect('/')
