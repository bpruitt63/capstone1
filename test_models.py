import os
from unittest import TestCase
from flask_bcrypt import Bcrypt
from sqlalchemy import exc
bcrypt = Bcrypt()

from models import db, User, Game, Review, Question, Answer, Upvote

os.environ['DATABASE_URL'] = "postgresql:///gamey_test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class UserModelTestCase(TestCase):
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Game.query.delete()
        Question.query.delete()
        Answer.query.delete()
        Review.query.delete()
        Upvote.query.delete()

        self.client = app.test_client()

        hashed_pwd = bcrypt.generate_password_hash("HASHED_PASSWORD").decode('UTF-8')

        u = User(
            email="test@test.com",
            username="testuser",
            password=hashed_pwd,
            first_name="test",
            last_name='user'
        )

        db.session.add(u)
        db.session.commit()
        self.username = u.username

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2",
            first_name='test',
            last_name='user2'
        )

        db.session.add(u2)
        db.session.commit()

        self.assertEqual(len(u2.reviews), 0)
        self.assertEqual(len(u2.upvotes), 0)
        self.assertEqual(len(u2.questions), 0)
        self.assertEqual(len(u2.answers), 0)

    def test_sign_up_good(self):
        """Does sign_up work?"""

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2",
            first_name='test',
            last_name='user2')
        
        db.session.add(u2)
        db.session.commit()

        self.assertEqual(u2.email, "test2@test.com")
        self.assertEqual(u2.username, "testuser2")
        self.assertEqual(u2.image_url, "/static/images/default_image.png")
        self.assertEqual(u2.bio, 'No bio yet')

    def test_signup_bad(self):
        """Does sign_up check for unique username?"""
        with self.assertRaises(exc.IntegrityError) as context:
            u2 = User.signup(
                email="test2@test.com",
                username="testuser",
                password="HASHED_PASSWORD2",
                first_name='test',
                last_name='user2')

            db.session.add(u2)
            db.session.commit()
 
            self.assertEqual(len(User.query.all(), 1))


    def test_authenticate(self):
        """Does authenticate work?"""

        user = User.query.get(self.username)
        username = "testuser",
        password = "HASHED_PASSWORD"
        resp = User.authenticate(username, password)

        self.assertEqual(resp, user)

    def test_authenticate_bad_name(self):
        """Does authenticate return false when bad username?"""

        username = "testusergdf",
        password = "HASHED_PASSWORD"
        resp = User.authenticate(username, password)

        self.assertEqual(resp, False)

    def test_authenticate_bad_pwd(self):
        """Does authenticate return false when bad password?"""

        username = "testuser",
        password = "HASHED_PASSWORDfads"
        resp = User.authenticate(username, password)

        self.assertEqual(resp, False)

