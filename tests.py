# -*- coding: utf8 -*-

from datetime import datetime
import os
import unittest

from requests import get

from config import BASE_DIRECTORY
from app import app, db
from app.models import User, Mood


class ModelTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_user_construction(self):
        pass

    def test_basic_mood_construction(self):
        pass

    def test_advanced_mood_construction(self):
        pass

    def test_multiple_moods_over_multiple_days(self):
        pass

    def if_user_has_answered_advanced_questions_recently(self):
        pass


class APITests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_unauthorized_access(self):
        pass

    def test_authorized_access(self):
        pass

def main():
    unittest.main()

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
