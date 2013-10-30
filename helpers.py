
from requests import get, post

import config
from app import db, models


'''
default role = 0
admin role = 1

It defaults to 0 because we don't want to accidentally make a user an admin.
'''
def change_user_role(user_id, role=0):
    query = db.session.query(models.User).filter(models.User.id == user_id)
    user = query.first()

    if user: user.role = role

    db.session.commit()

def create_database():
    db.create_all()

'''
Exchange the hourly token for an extended two month token.
'''
def extend_token(client_id, short_term_token):
    payload = {'grant_type': 'fb_exchange_token',
               'client_id': config.FB_APP_ID,
               'client_secret': config.FB_APP_SECRET,
               'fb_exchange_token': short_term_token}

    result = get('https://graph.facebook.com/oauth/access_token',
                 params=payload).content

    return result.split('=')[1].split('&')[0]

'''
Send a notifcation to the user.

This method specifies a default message,  but the message can be overriden.
'''
def send_notification(user_id, message='Hey, time to rate your mood for today!'):
    payload = {'access_token' : '{0}|{1}'.format(config.FB_APP_ID,
                                                 config.FB_APP_SECRET),
              'href' : '',
              'template' : message}

    post('https://graph.facebook.com/' + user_id + '/notifications',
         params=payload)
