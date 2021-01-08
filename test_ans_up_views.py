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


class AnsUpViewsTestCase(TestCase):
    """Test model for answer and upvote routes"""

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
        self.username2 = u2.username

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
            username=self.username
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

        ans = Answer(
            text='testanswer',
            question_id=self.question_id,
            username=self.username
        )

        db.session.add(ans)
        db.session.commit()
        self.answer_id = ans.id

        ans2 = Answer(
            text='testanswer2',
            question_id=self.question_id,
            username=self.username
        )

        db.session.add(ans2)
        db.session.commit()
        self.answer_id2 = ans2.id

        rupv = Upvote(
            username=self.username2,
            review_id=self.review_id
        )

        db.session.add(rupv)
        db.session.commit()
        self.r_upvote_id = rupv.id

        aupv = Upvote(
            username=self.username2,
            answer_id=self.answer_id
        )

        db.session.add(aupv)
        db.session.commit()
        self.a_upvote_id = aupv.id

    def tearDown(self):
        db.session.rollback()

    def test_show_answers(self):
        """Do answers show on question page"""

        with self.client as c:

            resp = c.get(f'/questions/{self.question_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testanswer', html)
            self.assertNotIn("<button class='likeAnswer btn btn-sm btn-outline-success'>", html)
            self.assertNotIn("Edit Answer", html)
            self.assertNotIn("Answer Question", html)

    def test_show_answers_logged_in(self):
        """Do correct options show on question page logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            resp = c.get(f'/questions/{self.question_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testanswer', html)
            self.assertNotIn("<button class='likeAnswer btn btn-sm btn-outline-success'>", html)
            self.assertIn("Edit Answer", html)
            self.assertIn("Answer Question", html)

    def test_show_answers_logged_in_other(self):
        """Do correct options show on question page logged in as other user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username2

            resp = c.get(f'/questions/{self.question_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testanswer', html)
            self.assertIn("<button class='unlikeAnswer btn btn-sm btn-outline-danger'>", html)
            self.assertNotIn("Edit Answer", html)
            self.assertIn("Answer Question", html)

    def test_post_answer(self):
        """Can you post new answer to database"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            url = f"/questions/{self.question_id}/answer"
            resp = c.post(url, json={
                                    "text": "testanswer2",
                                    "username": self.username,
                                    "question_id": self.question_id
                                    })

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertIsInstance(data['answer_id'], int)
            del data['answer_id']
            del data['timestamp']
            self.assertEqual(data, {'text': "testanswer2", 
                                    'username': self.username})
            self.assertEqual(Answer.query.count(), 3)


    def test_edit_answer(self):
        """Can you post answer edit to database"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            url = f"/answers/{self.answer_id}/edit"
            resp = c.patch(url, json={"text": "testanswer2"})

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {'text': "testanswer2"})
            self.assertEqual(Answer.query.count(), 2)

    def test_delete_answer(self):
        """Can you delete answer from database"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username

            url = f"/answers/{self.answer_id}/delete"
            resp = c.delete(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {"delete": "success"})

    def test_like_review(self):
        """Can you add a like on a review to database"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username2

            url = f"/reviews/{self.review_id2}/upvote"
            resp = c.post(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {'review': self.review_id2, 
                                    'username': self.username2})
            self.assertEqual(Upvote.query.count(), 3)

    def test_unlike_review(self):
        """Can you remove a like on a review from database"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username2

            url = f"/reviews/{self.review_id}/remove_upvote"
            resp = c.delete(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {'review': self.review_id})
            self.assertEqual(Upvote.query.count(), 1)

    def test_like_answer(self):
        """Can you add a like on an answer to database"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username2

            url = f"/answers/{self.answer_id2}/upvote"
            resp = c.post(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {'answer': self.answer_id2, 
                                    'username': self.username2})
            self.assertEqual(Upvote.query.count(), 3)

    def test_unlike_answer(self):
        """Can you remove a like on an answer from database"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = self.username2

            url = f"/answers/{self.answer_id}/remove_upvote"
            resp = c.delete(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {'answer': self.answer_id})
            self.assertEqual(Upvote.query.count(), 1)