from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

def get_hashed_pwd(password):
    """Use bcrypt to hash given password"""

    hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
    return hashed_pwd


class Upvote(db.Model):
    """Upvotes given by users to reviews or answers"""

    __tablename__ = 'upvotes'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    username = db.Column(db.String,
                    db.ForeignKey('users.username', ondelete='SET NULL'))

    review_id = db.Column(db.Integer,
                    db.ForeignKey('reviews.id', ondelete='CASCADE'))
    
    answer_id = db.Column(db.Integer,
                    db.ForeignKey('answers.id', ondelete='CASCADE'))


class Review(db.Model):
    """Reviews written by users about games"""

    __tablename__ = 'reviews'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    title = db.Column(db.String(50),
                    nullable=False)

    rating = db.Column(db.Float,
                    nullable=False)

    text = db.Column(db.String,
                    nullable=False)

    timestamp = db.Column(db.TIMESTAMP,
                    nullable = False,
                    default=db.func.now())

    game_id = db.Column(db.Integer,
                    db.ForeignKey('games.id', ondelete='CASCADE'),
                    nullable=False)
    
    username = db.Column(db.String,
                    db.ForeignKey('users.username', ondelete='SET NULL'))


    upvotes = db.relationship('Upvote', backref='review', cascade='all, delete')


class Answer(db.Model):
    """Answers given by users to questions"""

    __tablename__ = 'answers'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    text = db.Column(db.String,
                    nullable=False)

    timestamp = db.Column(db.TIMESTAMP,
                    nullable = False,
                    default=db.func.now())

    question_id = db.Column(db.Integer,
                    db.ForeignKey('questions.id', ondelete='CASCADE'),
                    nullable=False)
    
    username = db.Column(db.String,
                    db.ForeignKey('users.username', ondelete='SET NULL'))


    upvotes = db.relationship('Upvote', backref='answer', cascade='all, delete')



class Question(db.Model):
    """Questions asked by users about games"""

    __tablename__ = 'questions'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    title = db.Column(db.String(50),
                    nullable=False)

    text = db.Column(db.String,
                    nullable=False)

    timestamp = db.Column(db.TIMESTAMP,
                    nullable = False,
                    default=db.func.now())

    game_id = db.Column(db.Integer,
                    db.ForeignKey('games.id', ondelete='CASCADE'),
                    nullable=False)
    
    username = db.Column(db.String,
                    db.ForeignKey('users.username', ondelete='SET NULL'))


    answers = db.relationship('Answer', backref='question', cascade='all, delete')



class User(db.Model):
    """Registered users"""

    __tablename__ = 'users'

    username = db.Column(db.String(20),
                    primary_key=True)

    password = db.Column(db.String,
                    nullable=False)

    email = db.Column(db.String(30),
                    nullable=False)

    first_name = db.Column(db.String(20),
                    nullable=False)

    last_name = db.Column(db.String(20),
                    nullable=False)

    bio = db.Column(db.String)

    image_url = db.Column(db.String,
                    nullable=False,
                    default="/static/images/default_image.png")


    reviews = db.relationship('Review', backref='user')

    questions = db.relationship('Question', backref='user')

    answers = db.relationship('Answer', backref='user')

    upvotes = db.relationship('Upvote', backref='user')

        

    @classmethod
    def signup(cls, username, password, email, first_name, last_name):
        """Sign up user"""

        hashed_pwd = get_hashed_pwd(password)

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
            bio="No bio yet",
            image_url="/static/images/default_image.png"
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user, or return False"""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Game(db.Model):
    """Game info that has been accessed already"""

    __tablename__ = 'games'

    id = db.Column(db.Integer,
                    primary_key=True)

    name = db.Column(db.String,
                    nullable=False)

    background_image = db.Column(db.String)


    reviews = db.relationship('Review', backref='game', cascade='all, delete')

    questions = db.relationship('Question', backref='game', cascade='all, delete')


    @classmethod
    def add_game_to_db(cls, id, name, background_image):
        """Add newly accessed game to database"""

        new_game = Game(id=id,
                        name=name,
                        background_image=background_image)
        db.session.add(new_game)
        return new_game




