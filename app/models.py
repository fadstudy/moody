from datetime import datetime, timedelta

from flask import abort
from flask.ext.restful import Resource, fields, marshal

from app import auth, db
from config import LONG_TERM_TOKEN, SHORT_TERM_TOKEN, ROLE_ADMIN, ROLE_USER


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    facebook_id = db.Column(db.String(64), index=True, unique=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    consented = db.Column(db.Boolean, default=False)

    moods = db.relationship('Mood')
    tokens = db.relationship('Token')

    def get_short_term_token(self):
        try:
            return [t for t in self.tokens if t._type == SHORT_TERM_TOKEN][0]
        except IndexError:
            return None

    def set_short_term_token(self, token):
        try:
            self.tokens.remove(self.get_short_term_token())
        except ValueError:
            pass

        self.tokens.append(Token(token=token, token_type=SHORT_TERM_TOKEN))

    def get_long_term_token(self):
        try:
            return [t for t in self.tokens if t._type == LONG_TERM_TOKEN][0]
        except IndexError:
            return None

    def set_long_term_token(self, token):
        try:
            self.tokens.remove(self.get_long_term_token())
        except ValueError:
            pass

        self.tokens.append(Token(token=token, token_type=LONG_TERM_TOKEN))

    def needs_to_exchange_for_long_term_token(self):
        token = self.get_long_term_token()
        if token is None or (token.expiry_date - datetime.utcnow()).days <= 14:
            return True
        return False

    def is_admin(self):
        return True if user.role == ROLE_ADMIN else False

    def update_last_visit(self):
        self.last_visit = datetime.utcnow()

    def created_date_formatted(self):
        return (self.created_date + timedelta(hours=11)).strftime('%A, %B %d')

    def last_login_formatted(self):
        return (self.last_visit + timedelta(hours=11)).strftime('%A, %B %d')

    def has_answered_advanced_questions_recently(self):
        for mood in reversed(self.moods):
            # Check the last time these questions were answered.  The fields
            # will be None if unanswered (that's the default).
            if mood.medication >= 0 and mood.hospital >= 0:
                days_since_answer = ((datetime.utcnow() + timedelta(hours=11)) \
                                     - (mood.time_stamp +
                                        timedelta(hours=11))).days
                return False if days_since_answer >= 14 else True
        # If we reach this point it means the user hasn't answered the advanced
        # questions, so we return False.
        return False

    def latest_mood(self):
        try:
            latest_mood = self.moods[-1]
            if (latest_mood.time_stamp + timedelta(hours=11)).date() == \
                               (datetime.utcnow() + timedelta(hours=11)).date():
                return True
            return False
        except IndexError:
            return False

    def latest_mood_change(self):
        try:
            ultimate_mood = self.moods[-1].rating
            penultimate_mood = self.moods[-2].rating

            difference = ultimate_mood - penultimate_mood

            return difference
        except IndexError:
            return 0

    def average_mood(self):
        total_rating = 0
        for mood in self.moods:
            total_rating += mood.rating

        total_moods = 1 if len(self.moods) == 0 else len(self.moods)

        return total_rating / total_moods

    def response_rate(self):
        # Calculate the number of days since sign up
        delta = (datetime.utcnow() + timedelta(hours=11)) - \
                                       (self.created_date + timedelta(hours=11))

        moods = len(self.moods)
        days = delta.days

        if days == 0 or moods == 0:
            return 0.0

        if moods > days:
            return '{0:.3g}'.format((1 / 1) * 100)

        return '{0:.3g}'.format((moods / float(days)) * 100)

    def __repr__(self):
        return '<User {0}>'.format(self.id)


class Mood(db.Model):
    __tablename__ = 'moods'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    medication = db.Column(db.SmallInteger, default=0)
    medication_bipolar_related = db.Column(db.Boolean, default=False)
    hospital = db.Column(db.SmallInteger, default=0)
    hospital_bipolar_related = db.Column(db.Boolean, default=False)

    def unix_timestamp(self):
        return round(float(self.time_stamp.strftime('%s.%f')), 3)

    def __repr__(self):
        return '/api/v0.1/moods/{0}'.format(self.id)


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(512))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    _type = db.Column(db.SmallInteger)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, token, token_type):
        self.access_token = token
        self._type = token_type
        self.expiry_date = datetime.utcnow()

        if token_type == 1:
            self.expiry_date = self.expiry_date + timedelta(days=60)

    def __repr__(self):
        return 'Token: {0} - {1}'.format(self._type, self.expiry_date)


"""
API Models
"""

users_fields = {
    'created_date': fields.String,
    'facebook_id': fields.String,
    'last_visit': fields.String,
    'uri': fields.Url('User')
}

user_fields = {
    'created_date': fields.String,
    'facebook_id': fields.String,
    'moods': fields.Url('UserMoods'),
    'id': fields.String,
    'last_visit': fields.String,
    'tokens': fields.Url('UserTokens')
}

moods_fields = {
    'rating': fields.String,
    'time_stamp': fields.String,
    'uri': fields.Url('Mood')
}

mood_fields = {
    'id': fields.String,
    'rating': fields.String,
    'time_stamp': fields.String,
    'medication': fields.String,
    'medication_bipolar_related': fields.String,
    'hospital': fields.String,
    'hospital_bipolar_related': fields.String,
    'user_uri': fields.Url('User')
}

tokens_fields = {
    'access_token': fields.String,
    'type': fields.String(attribute='_type'),
    'uri': fields.Url('Token')
}

token_fields = {
    'id' : fields.String,
    'access_token' : fields.String,
    'created_date' : fields.String,
    'expiry_date' : fields.String,
    'type' : fields.String(attribute='_type'),
    'user_uri': fields.Url('User')
}


class UserListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(UserListAPI, self).__init__()

    def get(self):
        return { 'users': map(lambda u: marshal(u, users_fields),
                              User.query.all()) }


class UserAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(UserAPI, self).__init__()

    def get(self, id):
        user = db.session.query(User).filter(User.id == id).first()

        if not user:
            abort(404)

        return { 'user': marshal(user, user_fields) }


class UserMoodListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(UserMoodListAPI, self).__init__()

    def get(self, id):
        return { 'moods': map(lambda m: marshal(m, moods_fields),
                              Mood.query.filter(Mood.user_id == id).all()) }


class MoodListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(MoodListAPI, self).__init__()

    def get(self):
        return { 'moods': map(lambda m: marshal(m, moods_fields),
                              Mood.query.all()) }


class MoodAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(MoodAPI, self).__init__()

    def get(self, id):
        mood = db.session.query(Mood).filter(Mood.id == id).first()

        if not mood:
            abort(404)

        return { 'mood': marshal(mood, mood_fields) }


class UserTokenListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(UserTokenListAPI, self).__init__()

    def get(self, id):
        return { 'tokens': map(lambda t: marshal(t, tokens_fields),
                              Token.query.filter(Token.user_id == id).all()) }


class TokenListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(TokenListAPI, self).__init__()

    def get(self):
        return { 'tokens': map(lambda t: marshal(t, tokens_fields),
                              Token.query.all()) }


class TokenAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(TokenAPI, self).__init__()

    def get(self, id):
        token = db.session.query(Token).filter(Token.id == id).first()

        if not token:
            abort(404)

        return { 'token': marshal(token, token_fields) }
