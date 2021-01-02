import os
from unittest import TestCase

from models import db, User, Game, Review, Question, Answer, Upvote

os.environ['DATABASE_URL'] = "postgresql:///gamey_test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class ViewsTestCase(TestCase):
    """Test model for pretty much everything"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Game.query.delete()
        Question.query.delete()
        Answer.query.delete()
        Review.query.delete()
        Upvote.query.delete()

        self.client = app.test_client()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            first_name="test",
            last_name='user'
        )

        db.session.add(u)
        db.session.commit()
        self.username = u.username

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2",
            first_name="test2",
            last_name='user2'
        )

        db.session.add(u2)
        db.session.commit()

        game = Game(
            name='testgame',
            id=1,
            background_image='test_background_image'
        )

        db.session.add(game)
        db.session.commit()

        rev = Review(
            title='testreview',
            text="testtext",
            rating=9,
            game_id=1,
            username=self.username
        )

        db.session.add(rev)
        db.session.commit()
        self.review_id = rev.id

        rev2 = Review(
            title='testreview2',
            text="testtext2",
            rating=8,
            game_id=1,
            username='testuser2'
        )

        db.session.add(rev2)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()


    def test_show_profile_logged_out(self):
        """User profile page when not logged in"""

        with self.client as c:
            resp = c.get(f'/users/{self.username}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)
            self.assertNotIn('Edit Profile', html)

    def test_show_profile_logged_in(self):
        """User profile page when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.get(f'/users/{self.username}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)
            self.assertIn('Edit Profile', html)

    def test_show_other_profile_logged_in(self):
        """Other user profile page when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.get('/users/testuser2')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser2', html)
            self.assertNotIn('Edit Profile', html)

    def test_edit_user(self):
        """Can logged in user edit self"""
    
        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.post(f'/users/{self.username}/edit', 
                    data={'username': 'testuser99', 'password': 'HASHED_PASSWORD'}, 
                    follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser99', html)

    def test_edit_user_logged_out(self):
        """Can logged out user edit user"""
    
        with self.client as c:

            resp = c.post(f'/users/{self.username}/edit', 
                    data={'username': 'testuser99', 'password': 'HASHED_PASSWORD'}, 
                    follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_delete_user(self):
        """Can logged in user delete self"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username
            
            resp = c.post(f'/users/{self.username}/delete', 
                    data={'password': 'HASHED_PASSWORD'},
                    follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Game Over', html)
            self.assertNotIn(self.username, sess['username'])
            self.assertEqual(len(users), 1)