# -*- coding: utf8 -*-

from datetime import datetime
import os
import unittest

from coverage import coverage
cov = coverage(branch = True, omit = ['flask/*', 'tests.py'])
cov.start()

from config import BASE_DIRECTORY
from app import app, db
from app.models import User, Mood


class ModelTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIRECTORY, 'test.db')
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_construction(self):
        user = User(facebook_id='1234567')

        db.session.add(user)
        db.session.commit()

        assert user is not None
        assert user.role == 0
        assert user.latest_mood() == False
        assert user.latest_mood_change() == 0
        assert user.average_mood() == 0
        assert user.response_rate() == 0.0
        assert user.has_answered_advanced_questions_recently() == False

        user2 = None
        try:
            user2 = User(facebook_id='1234567')

            db.session.add(user2)
            db.session.commit()
        except:
            user2 = None

        assert user2 is None

    def test_mood_construction(self):
        facebook_id = '1234567'
        user = User(facebook_id=facebook_id)

        db.session.add(user)
        db.session.commit()

        assert user is not None
        assert len(user.moods) == 0

        mood = Mood(rating=10)

        user.moods.append(mood)
        db.session.commit()

        assert len(user.moods) == 1

        assert mood.rating == 10
        assert mood.time_stamp.hour == datetime.utcnow().hour
        assert mood.medication == 0
        assert mood.medication_bipolar_related == False
        assert mood.hospital == 0
        assert mood.hospital_bipolar_related == False

def main():
    unittest.main()

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass

    '''
    Uncomment for coverage reports
    '''
    # cov.stop()
    # cov.save()
    # print "\n\nCoverage Report:\n"
    # cov.report()
    # print "\nHTML version: " + os.path.join(BASE_DIRECTORY,
    #                                         "tmp/coverage/index.html")
    # cov.html_report(directory = 'tmp/coverage')
    # cov.erase()
