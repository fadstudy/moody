
import requests

from app import db, models
import config


def send_notification(user_id):
    payload = {'access_token' : '{0}|{1}'.format(config.FB_APP_ID,
                                                 config.FB_APP_SECRET),
              'href' : '',
              'template' : 'Hey, time to rate your mood for today!'}

    requests.post('https://graph.facebook.com/' + user_id + '/notifications',
                  params=payload)

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
