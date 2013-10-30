
import unittest

from requests import get, post

from app import db, models

# http://www.openp2p.com/pub/a/python/2004/12/02/tdd_pyunit.html

class UserTests(unittest.TestCase):
    def testUserConstruction(self):
        pass

    def testCreatedDate(self):
        pass

    def testLastLogIn(self):
        pass

    def testLatestMood(self):
        pass

    def testAverageMood(self):
        pass

    def testResponseRate(self):
        pass

    def testLatestMoodChange(self):
        pass


class MoodTests(unittest.TestCase):
    def testMoodSubmission(self):
        payload = {'mood-radio' : '2',
                   'hosptial-radio': '1',
                   'medication-radio': '1',
                   'user-id' : '1000'}

        response = post('http://localhost:5001/moods/new', params=payload)

        print response.content

    def testMoodValidation(self):
        pass


def main():
    unittest.main()

if __name__ == '__main__':
    main()