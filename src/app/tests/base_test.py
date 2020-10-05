"""
BaseTest
This class should be the parent class to each unit test.
It allows for instantiation of the database dynamically,
and makes sure that it is a new, blank database each time.
"""

from unittest import TestCase
from run import app
from db import db


class BaseTest(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"

    @classmethod
    def setUpClass(cls):
        """
        Runs once for each test case
        """
        app.config["SQLALCHEMY_DATABASE_URI"] = BaseTest.SQLALCHEMY_DATABASE_URI
        app.config["DEBUG"] = False
        with app.app_context():
            db.init_app(app)

    def setUp(self):
        """
        Checks if database exists
        Runs for each test method
        """
        with app.app_context():
            db.create_all()
        self.app = app.test_client
        self.app_context = app.app_context

    def tearDown(self):
        """
        Blanks database
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()