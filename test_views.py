import os
from unittest import TestCase
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

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

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password=hashed_pwd,
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
        self.review_id2 = rev2.id

        q = Question(
            title='testquestion',
            text="testtext",
            game_id=1,
            username=self.username
        )

        db.session.add(q)
        db.session.commit()
        self.question_id = q.id

        q2 = Question(
            title='testquestion2',
            text="testtext2",
            game_id=1,
            username='testuser2'
        )

        db.session.add(q2)
        db.session.commit()
        self.question_id2 = q2.id

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
                    data={'bio': 'testbioedit', 'password': 'HASHED_PASSWORD'}, 
                    follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testbioedit', html)

    def test_edit_user_logged_out(self):
        """Can logged out user edit user"""
    
        with self.client as c:

            resp = c.post(f'/users/{self.username}/edit', 
                    data={'bio': 'testbioedit', 'password': 'HASHED_PASSWORD'}, 
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
            users = User.query.all()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Game Over', html)
            self.assertEqual(len(users), 1)

    def test_show_game_reviews(self):
        """Are reviews listed on reviews page"""

        with self.client as c:

            resp = c.get('/games/1/reviews')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testreview', html)
            self.assertIn('testreview2', html)
            self.assertIn('Average User Rating: 8.5', html)
            self.assertNotIn('Add A Review', html)

    def test_add_review_logged_out(self):
        """Can you add a review when logged out"""

        with self.client as c:

            resp = c.post('/games/1/review',
                    data={'title': 'testreview3',
                            'rating': 1.4,
                            'text': 'testreviewtext3',
                            'game_id': 1},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You must be logged in to write a review', html)

    def test_add_review_logged_in(self):
        """Can you add a review when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.post('/games/1/review',
                    data={'title': 'testreview3',
                            'rating': 1.4,
                            'text': 'testreviewtext3',
                            'game_id': 1},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Thanks for reviewing', html)
            self.assertIn('testreview3', html)
            self.assertIn('testreview2', html)
            self.assertIn('Average User Rating: 6', html)

    def test_show_review(self):
        """Does it show single review"""

        with self.client as c:

            resp = c.get(f'/reviews/{self.review_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testgame', html)
            self.assertIn('testtext', html)
            self.assertNotIn('Edit Review', html)

    def test_edit_review_logged_out(self):
        """Can logged out user edit review"""

        with self.client as c:

            resp = c.post(f'/reviews/{self.review_id}/edit',
                    data={'title': 'testreview3',
                            'rating': 1.4,
                            'text': 'testreviewtext3'},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("author can edit a review", html)

    def test_edit_review_logged_in(self):
        """Can you edit a review when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.post(f'/reviews/{self.review_id}/edit',
                    data={'title': 'testreview3',
                            'rating': 1.4,
                            'text': 'testreviewtext3'},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testreviewtext3', html)
            self.assertIn('testreview3 - 1.4', html)

    def test_edit_wrong_review(self):
        """Can you edit a review written by someone else"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.post(f'/reviews/{self.review_id2}/edit',
                    data={'title': 'testreview3',
                            'rating': 1.4,
                            'text': 'testreviewtext3'},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("author can edit a review", html)

    def test_delete_review(self):
        """Can you delete a review"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            url = f"/reviews/{self.review_id}/delete"
            resp = c.delete(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {"game_id": 1})

    def test_show_game_questions(self):
        """Are questions listed on questions page"""

        with self.client as c:

            resp = c.get('/games/1/questions')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testquestion', html)
            self.assertIn('testquestion2', html)
            self.assertNotIn('Ask A Question', html)

    def test_add_question_logged_out(self):
        """Can you add a question when logged out"""

        with self.client as c:

            resp = c.post('/games/1/question',
                    data={'title': 'testquestion3',
                            'text': 'testquestiontext3',
                            'game_id': 1},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You must be logged in to ask a question', html)

    def test_add_question_logged_in(self):
        """Can you add a question when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.post('/games/1/question',
                    data={'title': 'testquestion3',
                            'text': 'testquestiontext3',
                            'game_id': 1},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Thanks for your question', html)
            self.assertIn('testquestion3', html)
            self.assertIn('testquestion2', html)
            self.assertIn('Ask A Question', html)

    def test_show_question(self):
        """Does it show single question"""

        with self.client as c:

            resp = c.get(f'/questions/{self.question_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testgame', html)
            self.assertIn('testtext', html)
            self.assertNotIn('Edit Question', html)

    def test_edit_question_logged_out(self):
        """Can logged out user edit question"""

        with self.client as c:

            resp = c.post(f'/questions/{self.question_id}/edit',
                    data={'title': 'testquestion3',
                            'text': 'testquestiontext3'},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("author can edit a question", html)

    def test_edit_question_logged_in(self):
        """Can you edit a question when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.post(f'/questions/{self.question_id}/edit',
                    data={'title': 'testquestion3',
                            'text': 'testquestiontext3'},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testquestiontext3', html)
            self.assertIn('testquestion3', html)

    def test_edit_wrong_question(self):
        """Can you edit a question written by someone else"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.post(f'/questions/{self.question_id2}/edit',
                    data={'title': 'testquestion3',
                            'text': 'testquestiontext3'},
                            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("author can edit a question", html)

    def test_delete_question(self):
        """Can you delete a question"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            url = f"/questions/{self.question_id}/delete"
            resp = c.delete(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {"game_id": 1})