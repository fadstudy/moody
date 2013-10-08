
import base64
import os
import os.path
import urllib
import hmac
import json
import hashlib
import datetime
from base64 import urlsafe_b64decode, urlsafe_b64encode

import requests
from flask import Flask, request, redirect, render_template, url_for

from app import app, db
from models import User, Mood, Token

# TODO: Remove hardcoded ID
FB_APP_ID = 498777246878058
# FB_APP_ID = os.environ.get('FACEBOOK_APP_ID')
requests = requests.session()

app_url = 'https://graph.facebook.com/{0}'.format(FB_APP_ID)
FB_APP_NAME = 'The FAD Study'
# FB_APP_NAME = json.loads(requests.get(app_url).content).get('name')
# TODO: Remove hardcoded ID
FB_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'
# FB_APP_SECRET = os.environ.get('FACEBOOK_SECRET')

def oauth_login_url(preserve_path=True, next_url=None):
    fb_login_uri = ("https://www.facebook.com/dialog/oauth"
                    "?client_id=%s&redirect_uri=%s" %
                    (app.config['FB_APP_ID'], get_home()))

    if app.config['FBAPI_SCOPE']:
        fb_login_uri += "&scope=%s" % ",".join(app.config['FBAPI_SCOPE'])

    return fb_login_uri


def simple_dict_serialisation(params):
    return "&".join(map(lambda k: "%s=%s" % (k, params[k]), params.keys()))


def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip('=')


def fbapi_get_string(path,
    domain=u'graph', params=None, access_token=None,
    encode_func=urllib.urlencode):
    """Make an API call"""

    if not params:
        params = {}
    params[u'method'] = u'GET'
    if access_token:
        params[u'access_token'] = access_token

    for k, v in params.iteritems():
        if hasattr(v, 'encode'):
            params[k] = v.encode('utf-8')

    url = u'https://' + domain + u'.facebook.com' + path
    params_encoded = encode_func(params)
    url = url + params_encoded
    result = requests.get(url).content

    return result


def fbapi_auth(code):
    params = {'client_id': app.config['FB_APP_ID'],
              'redirect_uri': get_home(),
              'client_secret': app.config['FB_APP_SECRET'],
              'code': code}

    result = fbapi_get_string(path=u"/oauth/access_token?", params=params,
                              encode_func=simple_dict_serialisation)
    pairs = result.split("&", 1)
    result_dict = {}
    for pair in pairs:
        (key, value) = pair.split("=")
        result_dict[key] = value
    return (result_dict["access_token"], result_dict["expires"])


def fbapi_get_application_access_token(id):
    # token = fbapi_get_string(
    #     path=u"/oauth/access_token",
    #     params=dict(grant_type=u'client_credentials', client_id=id,
    #                 client_secret=app.config['FB_APP_SECRET']),
    #     domain=u'graph')

    token = fbapi_get_string(
        path=u"/oauth/access_token",
        params=dict(grant_type=u'client_credentials',
                    client_id=id,
                    client_secret=app.config['FB_APP_SECRET'],
                    access_token='CAAHFoqCfSWoBAAVb4ICZAhiZAKMk46QMo6ESHQFhx3XHHKiVBr6XiPsgvsmmZB4k4KUJDA4uySf0JrtcjnujdsZBZBCyhCRkHtl3dOu8bnKCNg0DPBoJy8JL7t5tUdXAHxz4TZC0W0ZBbMVZCkrgdquqCJiDBaTIiEExfiu0ExTOfMNZBrlmxk50K5s88697rBTfnZCwqEhkLxTgZDZD'),
        domain=u'graph')

    token = token.split('=')[-1]
    if not str(id) in token:
        print 'Token mismatch: %s not in %s' % (id, token)
    return token


def fql(fql, token, args=None):
    if not args:
        args = {}

    args["query"], args["format"], args["access_token"] = fql, "json", token

    url = "https://api.facebook.com/method/fql.query"

    r = requests.get(url, params=args)
    return json.loads(r.content)


def fb_call(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.get(url, params=args)
    return json.loads(r.content)

def get_home():
    return 'https://' + request.host + '/'


def get_token():

    if request.args.get('code', None):
        return fbapi_auth(request.args.get('code'))[0]

    cookie_key = 'fbsr_{0}'.format(FB_APP_ID)

    if cookie_key in request.cookies:

        c = request.cookies.get(cookie_key)
        encoded_data = c.split('.', 2)

        sig = encoded_data[0]
        data = json.loads(urlsafe_b64decode(str(encoded_data[1]) +
            (64-len(encoded_data[1])%64)*"="))

        if not data['algorithm'].upper() == 'HMAC-SHA256':
            raise ValueError('unknown algorithm {0}'.format(data['algorithm']))

        h = hmac.new(FB_APP_SECRET, digestmod=hashlib.sha256)
        h.update(encoded_data[1])
        expected_sig = urlsafe_b64encode(h.digest()).replace('=', '')

        if sig != expected_sig:
            raise ValueError('bad signature')

        code =  data['code']

        params = {
            'client_id': FB_APP_ID,
            'client_secret': FB_APP_SECRET,
            'redirect_uri': '',
            'code': data['code']
        }

        from urlparse import parse_qs
        r = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        token = parse_qs(r.content).get('access_token')

        return token

def is_admin(access_token):
    print 'check admin', access_token

    if access_token:
        me = fb_call('me', args={'access_token': access_token})

        # If the token exists, check if the user has an admin role
        query = db.session.query(User).filter(User.facebook_id == me['id'])
        user = query.first()

        print user.id

        if user:
            # If the user is an admin
            if user.role == 1:
                return True

    return False

@app.route('/admin/', methods=['GET'])
def admin():
    # Grab the session's access token
    access_token = get_token()

    if is_admin(access_token) == True:
        query = db.session.query(User)
        users = query.all()

        me = fb_call('me', args={'access_token': access_token})
        query = db.session.query(User).filter(User.facebook_id == me['id'])
        user = query.first()
        return render_template('admin.html', name=FB_APP_NAME, me=me, users=users, user=user)
    else:
        return redirect('/')

@app.route('/users/<int:user_id>/')
@app.route('/users/<int:user_id>')
def user(user_id):
    # Grab the session's access token
    access_token = get_token()

    if is_admin(access_token) == True:
        me = fb_call('me', args={'access_token': access_token})
        query = db.session.query(User).filter(User.facebook_id == user_id)
        user = query.first()

        return render_template('users.html', user=user, me=me)
    else:
        return redirect('/')


def extend_token(client_id, short_term_token):
    payload = {'grant_type': 'fb_exchange_token',
               'client_id': FB_APP_ID,
               'client_secret': FB_APP_SECRET,
               'fb_exchange_token': short_term_token}

    result = requests.get('https://graph.facebook.com/oauth/access_token', params=payload).content

    return result.split('=')[1].split('&')[0]

@app.route('/moods/', methods=['POST'])
def submit_mood():
    mood = request.form['mood-radio']
    user_id = request.form['user-id']

    query = db.session.query(User).filter(User.facebook_id == user_id)
    user = query.first()
    user.moods.append(
        Mood(rating=mood)
    )
    db.session.commit()

    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():

    date = datetime.datetime.now().strftime('%A, %B %d')

    access_token = get_token()
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    if access_token:

        me = fb_call('me', args={'access_token': access_token})

        query = db.session.query(User).filter(User.facebook_id == me['id'])
        user = query.first()

        if user is None:
            user = User(facebook_id=me['id'])
            extended_token = extend_token(me['id'], access_token)
            user.tokens.append(Token(access_token=extended_token))
            db.session.add(user)
            db.session.commit()
        else:
            # Check access token
            # If close to expiration extend
            user.last_vist = datetime.datetime.utcnow()
            db.session.commit()


        # print extend_token(me['id'], access_token)

        # flag = False
        # with open('users.txt', 'rt') as _file:
        #     next(_file)
        #     for line in _file:
        #         fields = line.split(',')
        #         if me['id'] == fields[0]:
        #             flag = True

        # if flag is False:
        #     fields = [me['id'], access_token[0], datetime.datetime.now(), datetime.datetime.now(), False]
        #     with open('users.txt', 'a') as _file:
        #         _file.write(','.join(str(field) for field in fields))

        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
        # likes = fb_call('me/likes',
        #                 args={'access_token': access_token, 'limit': 4})
        # friends = fb_call('me/friends',
        #                   args={'access_token': access_token, 'limit': 4})
        # photos = fb_call('me/photos',
        #                  args={'access_token': access_token, 'limit': 16})

        redir = get_home() + 'close/'
        POST_TO_WALL = ("https://www.facebook.com/dialog/feed?redirect_uri=%s&"
                        "display=popup&app_id=%s" % (redir, FB_APP_ID))

        # app_friends = fql(
        #     "SELECT uid, name, is_app_user, pic_square "
        #     "FROM user "
        #     "WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me()) AND "
        #     "  is_app_user = 1", access_token)

        SEND_TO = ('https://www.facebook.com/dialog/send?'
                   'redirect_uri=%s&display=popup&app_id=%s&link=%s'
                   % (redir, FB_APP_ID, get_home()))

        url = request.url

        # print str(access_token[0])

        return render_template(
            'index.html', app_id=FB_APP_ID, token=access_token, app=fb_app,
            me=me, POST_TO_WALL=POST_TO_WALL, SEND_TO=SEND_TO, url=url,
            channel_url=channel_url, name=FB_APP_NAME, date=date, chungus=str(access_token[0]), user=user)
    else:
        return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME, date=date)

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')


@app.route('/close/', methods=['GET', 'POST'])
def close():
    return render_template('close.html')
