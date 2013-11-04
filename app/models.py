from datetime import datetime, timedelta

from app import db

ROLE_USER = 0
ROLE_ADMIN = 1
SHORT_TOKEN = 0
LONG_TOKEN = 1

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    facebook_id = db.Column(db.String(64), index=True, unique=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    short_term_access_token = db.Column(db.String(512))

    moods = db.relationship('Mood')
    tokens = db.relationship('Token')

    def get_access_token(self):
        return self.short_term_access_token
        # return self.tokens[0].access_token

    def created_date_formatted(self):
        return (self.created_date + timedelta(hours=11)).strftime('%A, %B %d')

    def last_login_formatted(self):
        return (self.last_visit + timedelta(hours=11)).strftime('%A, %B %d')

    def has_answered_advanced_questions_recently(self):
        for mood in reversed(self.moods):
            # Check the last time these questions were answered.  The fields
            # will be None if unanswered (that's the default).
            if mood.medication and mood.hospital:
                days_since_answer = ((datetime.utcnow() + timedelta(hours=11)) - \
                    (mood.time_stamp + timedelta(hours=11))).days
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

            if difference == 0:
                return '-'
            elif difference > 0:
                return '+{0}'.format(str(difference))
            else:
                return difference
        except IndexError:
            return '-'

    def average_mood(self):
        total_rating = 0
        for mood in self.moods:
            total_rating += mood.rating

        moods = len(self.moods)
        if moods is 0:
            moods = 1

        return total_rating / moods

    def response_rate(self):
        # Calculate the number of days since sign up
        delta = (datetime.utcnow() + timedelta(hours=11)) - \
                                       (self.created_date + timedelta(hours=11))

        moods = 1 if len(self.moods) == 0 else len(self.moods)
        days = 1 if delta.days == 0 else delta.days

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
    medication = db.Column(db.SmallInteger, default=None)
    medication_bipolar_related = db.Column(db.Boolean, default=None)
    hospital = db.Column(db.SmallInteger, default=None)
    hospital_bipolar_related = db.Column(db.Boolean, default=None)

    def unix_timestamp(self):
        return round(float(self.time_stamp.strftime('%s.%f')), 3)

    def __repr__(self):
        return '\'{0}\': {1}'.format(self.unix_timestamp(), self.rating)


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(512))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    _type = db.Column(db.SmallInteger, default=LONG_TOKEN)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, access_token):
        self.access_token = access_token
        # Set the expiry from 2 months from now
        self.expiry_date = datetime.utcnow() + timedelta(hours=720)
