# -*- coding: utf8 -*-

from datetime import datetime
import os
import unittest

from coverage import coverage
cov = coverage(branch = True, omit = ['flask/*', 'tests.py'])
cov.start()
from requests import get

from config import BASE_DIRECTORY
from app import app, db
from app.models import User, Mood

'''
TODO:
Inherit from a base class that handles the setUp and tearDown methods
'''

class ModelTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIRECTORY, 'test.db')
        app.config['debug'] = True
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

    def test_basic_mood_construction(self):
        user = User(facebook_id='1234567')

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
        assert user.has_answered_advanced_questions_recently() == False

    def test_advanced_mood_construction(self):
        user = User(facebook_id='1234567')

        db.session.add(user)
        db.session.commit()

        assert user is not None
        assert len(user.moods) == 0

        mood = Mood(rating=10, medication=1, hospital=1,
                    medication_bipolar_related=True,
                    hospital_bipolar_related=True)

        user.moods.append(mood)
        db.session.commit()

        assert len(user.moods) == 1

        assert mood.rating == 10
        assert mood.time_stamp.hour == datetime.utcnow().hour
        assert mood.medication == 1
        assert mood.medication_bipolar_related == True
        assert mood.hospital == 1
        assert mood.hospital_bipolar_related == True

    def test_multiple_moods_over_multiple_days(self):
        pass

    def if_user_has_answered_advanced_questions_recently(self):
        pass


class APITests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIRECTORY, 'test.db')
        app.config['debug'] = True
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_unauthorized_access(self):
        response = get('http://localhost:5000/api/v0.1/users')

        assert response is not None
        assert response.status_code == 403

        response = get('http://localhost:5000/api/v0.1/users', auth=('user',
                                                                     'pass'))

        assert response is not None
        assert response.status_code == 403

    def test_authorized_access(self):
        response = get('http://localhost:5000/api/v0.1/users',
                       auth=('apiuser', 'letmeinbrah!'))

        assert response is not None
        assert response.status_code == 200

    # TODO: Figure out how to get the API to serve the test database so we can
    # control and test the data returned...


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
