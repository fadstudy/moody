import facebook
from flask import request, url_for
from requests import get

from app import db
from config import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from models import User

def channel():
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    return channel_url

def exchange_token(short_term_token):
    """ Exchange a short term token for a long term token through Facebook."""
    payload = { 'grant_type': 'fb_exchange_token',
                'client_id': FACEBOOK_APP_ID,
                'client_secret': FACEBOOK_APP_SECRET,
                'fb_exchange_token': short_term_token }

    response = get('https://graph.facebook.com/oauth/access_token',
                   params=payload).content

    """
    TODO (Mitch):
    When the key exchange goes bad (the only case where I've encountered this
    happening is with the Facebook test users) we need to handle this error
    response.
    """
    return response.split('=')[1].split('&')[0]

def get_current_user():
    """Get the currently logged in user."""

    # Get user id and access token from the client's cookie.
    token = facebook.get_user_from_cookie(request.cookies, FACEBOOK_APP_ID,
                                          FACEBOOK_APP_SECRET)

    try:
        user = User.query.filter(User.facebook_id == token['uid']).first()

        if not user:
            # If the user doesn't exist, add them to the database.
            user = User(facebook_id=token['uid'])
            db.session.add(user)

            # Set the user's access tokens
            user.set_short_term_token(token=token['access_token'])
            user.set_long_term_token(token=
                                     exchange_token(token['access_token']))
        else:
            # Update the user's short term access token.
            user.set_short_term_token(token=token['access_token'])
            # Update user's long term access token, if need be.
            if user.needs_to_exchange_for_long_term_token():
                user.set_long_term_token(token=
                                         exchange_token(token['access_token']))

            user.update_last_visit()
    except:
        # We know the user exists in the database, so grab them.
        user = User.query.filter(User.facebook_id == token).first()
        if user:
            user.update_last_visit()

    # Save all the changes we've made and return the user
    db.session.commit()
    return user