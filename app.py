from flask import Flask, redirect, render_template, flash, session, request
import os
import requests
import json
import statistics
import copy
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, get_hashed_pwd, readable_time, readable_times, User, Game, Review, Question, Answer, Upvote
#from secrets import headers
from forms import RegisterForm, LoginForm, UserEditForm, ReviewForm, QuestionForm, DeleteUserForm
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secsecsecretret')
#debug = DebugToolbarExtension(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///gamey')
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

#BASE_URL = "https://rawg-video-games-database.p.rapidapi.com/games"
BASE_URL = 'https://api.rawg.io/api/games'
#head = os.environ.get('HEADERS')
API_KEY = os.environ.get('API_KEY')
# headers = json.loads(head)

def login(user):
        """Add user to session"""

        session['username'] = user.username

def logout():
        """Remove user from session"""

        session.pop('username')

@app.route('/')
def show_homepage():
    """Show homepage"""

    reviews = db.session.query(Review).order_by(Review.id.desc()).limit(5)
    reviews = list(reviews)
    reviews = readable_times(reviews)
    questions = db.session.query(Question).order_by(Question.id.desc()).limit(5)
    questions = list(questions)
    questions = readable_times(questions)
    
    return render_template('home.html', reviews=reviews, questions=questions)


################## User Routes #######################

@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Display registration form and submit new user registration"""

    if 'username' in session:
        return redirect("/")

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            db.session.commit()
            login(user)
            return redirect("/")

        except IntegrityError:
            flash("Username not available")
            return render_template('users/register.html', form=form)

    return render_template('users/register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Display login form and validate login"""

    if 'username' in session:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            login(user)
            flash(f"Hello, {user.username}!")
            return redirect("/")

        flash("Invalid credentials.")

    return render_template('users/login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout_user():
    """Logout user"""

    logout()
    flash('Happy gaming!')
    return redirect('/login')

@app.route('/users/<username>')
def show_user_profile(username):
    """Show individual user's profile details"""

    user = User.query.get_or_404(username)
    user.reviews = readable_times(user.reviews)
    user.reviews = sorted(user.reviews, reverse=True, key=lambda o: o.id)
    user.questions = readable_times(user.questions)
    user.questions = sorted(user.questions, reverse=True, key=lambda o: o.id)
    ques = []
    for answer in user.answers:
        ques.append(answer.question)
    ques = list(dict.fromkeys(ques))
    ques = sorted(ques, reverse=True, key=lambda o: o.id)
    return render_template('users/profile.html', user=user, ques=ques)

@app.route('/users/<username>/edit', methods=["GET", "POST"])
def edit_user(username):
    """Render form to edit user and handle form submission"""

    u = User.query.get_or_404(username)
    if ('username' not in session) or (session['username'] != u.username):
        flash("Access unauthorized")
        return redirect("/")

    form = UserEditForm(obj=u)

    if form.validate_on_submit():
        user = User.authenticate(u.username,
                                 form.password.data)

        if user:
            if form.email.data:
                user.email = form.email.data
            if form.image_url.data:
                user.image_url = form.image_url.data
            if form.bio.data:
                user.bio = form.bio.data
            if form.new_password.data:
                hashed_pwd = get_hashed_pwd(form.new_password.data)
                user.password = hashed_pwd

            db.session.commit()
            return redirect(f'/users/{user.username}')
        else:
            flash('Username and password do not match')
            return redirect(f'/users/{u.username}/edit')
    else:
        return render_template('users/edit.html', form=form, user=u)

@app.route('/users/<username>/delete', methods=['GET', 'POST'])
def delete_user(username):
    """Delete current user"""

    user = User.query.get_or_404(username)
    if ('username' not in session) or (session['username'] != user.username):
        flash("Access unauthorized")
        return redirect("/")

    form = DeleteUserForm()

    if form.validate_on_submit():
        user = User.authenticate(user.username,
                                 form.password.data)

        logout()

        db.session.delete(user)
        db.session.commit()

        flash('Game Over')

        return redirect("/")

    return render_template('users/delete.html', form=form, user=user)


################# Game Routes #####################

@app.route('/games/search')
def search_games():
    """Search game title and display list of possible matches"""

    game = request.args['game']
    #resp = requests.get(f'{BASE_URL}?search={game}', headers=headers)
    resp = requests.get(f'{BASE_URL}?key={API_KEY}&search={game}')
    resp = json.loads(resp.text)
    games = resp["results"]
    return render_template('games/results.html', games=games)

@app.route('/games/<game_id>')
def show_game_info(game_id):
    """Show information about a specific game"""

    game = Game.query.filter_by(id=game_id).first()
    
    #resp = requests.get(f'{BASE_URL}/{game_id}', headers=headers)
    resp = requests.get(f'{BASE_URL}/{game_id}?key={API_KEY}')
    game_api_data = json.loads(resp.text)

    if game:
        return render_template('games/info.html', game=game, game_api_data=game_api_data)

    new_game = Game.add_game_to_db(
                    id=game_id, 
                    name=game_api_data['name'], 
                    background_image=game_api_data['background_image'])

    db.session.commit()
    return render_template('games/info.html', game=new_game, game_api_data=game_api_data)

@app.route('/games/<game_id>/screenshots')
def show_screenshots(game_id):
    """Show all screenshots for a game"""

    game = Game.query.filter_by(id=game_id).first()
    #resp = requests.get(f'{BASE_URL}/{game_id}/screenshots', headers=headers)
    resp = requests.get(f'{BASE_URL}/{game_id}/screenshots?key={API_KEY}')
    screenshots = json.loads(resp.text)
    screenshots = screenshots['results']

    if game:
        return render_template('games/screenshots.html', game=game, screenshots=screenshots)

    resp = requests.get(f'{BASE_URL}/{game_id}', headers=headers)
    game_api_data = json.loads(resp.text)
    new_game = Game.add_game_to_db(
                    id=game_id, 
                    name=game_api_data['name'], 
                    background_image=game_api_data['background_image'])

    db.session.commit()
    return render_template('games/screenshots.html', game=new_game, screenshots=screenshots)


####################### Review Routes ###########################

@app.route('/games/<game_id>/reviews')
def show_game_reviews(game_id):
    """Show list of reviews for a specific game"""

    game = Game.query.filter_by(id=game_id).first()
    reviews = game.reviews
    reviews = readable_times(reviews)
    reviews = sorted(reviews, reverse=True, key=lambda o: o.id)
    ratings = []
    for review in game.reviews:
        ratings.append(review.rating)
    if ratings:
        average = round(statistics.mean(ratings), 2)
    else:
        average = "No ratings yet"

    if game:
        return render_template('games/reviews.html', game=game, average=average, reviews=reviews)

    resp = requests.get(f'{BASE_URL}/{game_id}', headers=headers)
    game_api_data = json.loads(resp.text)
    new_game = Game.add_game_to_db(
                    id=game_id, 
                    name=game_api_data['name'], 
                    background_image=game_api_data['background_image'])

    db.session.commit()
    return render_template('games/reviews.html', game=new_game, average=average, reviews=reviews)

@app.route('/games/<game_id>/review', methods=['GET', 'POST'])
def add_review(game_id):
    """Add a review for the selected game"""

    if 'username' not in session:
        flash("You must be logged in to write a review")
        return redirect(f"/games/{game_id}/reviews")

    game = Game.query.filter_by(id=game_id).first()
    user = User.query.get_or_404(session['username'])
    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(title=form.title.data,
                        rating=round(form.rating.data, 1),
                        text=form.text.data,
                        game_id=game_id,
                        username=user.username)
        
        db.session.add(review)
        db.session.commit()

        flash(f'Thanks for reviewing {game.name}')
        return redirect(f'/games/{game_id}/reviews')

    return render_template('/games/add_review.html', form=form, game=game, user=user)

@app.route('/reviews/<review_id>')
def show_review(review_id):
    """Show the selected review"""

    review = Review.query.get_or_404(review_id)
    review = readable_time(review)
    upvotes = []
    for upvote in review.upvotes:
        upvotes.append(upvote.username)

    return render_template('games/review.html', review=review, game=review.game, upvotes=upvotes)

@app.route('/reviews/<review_id>/edit', methods=["GET", "POST"])
def edit_review(review_id):
    """Display form to edit review and handle form submission"""

    review = Review.query.get_or_404(review_id)

    if ('username' not in session) or (session['username'] != review.username):
        flash("Only a review's author can edit a review")
        return redirect(f"/")

    form = ReviewForm(obj=review)

    if form.validate_on_submit():
        if form.title.data:
            review.title = form.title.data
        if form.rating.data:
            review.rating = form.rating.data
        if form.text.data:
            review.text = form.text.data

        db.session.commit()
        return redirect(f'/reviews/{review.id}')

    return render_template('games/edit_review.html', form=form, review=review, game=review.game)

@app.route('/reviews/<review_id>/delete', methods=['DELETE'])
def delete_review(review_id):
    """Delete review from database"""

    review = Review.query.get_or_404(review_id)
    game_id = copy.deepcopy(review.game_id)

    if ('username' not in session) or (session['username'] != review.username):
        flash("You can only delete your own review")
        return redirect('/')

    db.session.delete(review)
    db.session.commit()

    resp = {'game_id': game_id}
    return resp


##################### Question Routes ##########################

@app.route('/games/<game_id>/questions')
def show_game_questions(game_id):
    """Show list of questions for a specific game"""

    game = Game.query.filter_by(id=game_id).first()
    questions = game.questions
    questions = readable_times(questions)
    questions = sorted(questions, reverse=True, key=lambda o: o.id)

    if game:
        return render_template('games/questions.html', game=game, questions=questions)

    resp = requests.get(f'{BASE_URL}/{game_id}', headers=headers)
    game_api_data = json.loads(resp.text)
    new_game = Game.add_game_to_db(
                    id=game_id, 
                    name=game_api_data['name'], 
                    background_image=game_api_data['background_image'])

    db.session.commit()
    return render_template('games/questions.html', game=new_game, questions=questions)

@app.route('/games/<game_id>/question', methods=['GET', 'POST'])
def add_question(game_id):
    """Add a question for the selected game"""

    if 'username' not in session:
        flash("You must be logged in to ask a question")
        return redirect(f"/games/{game_id}/questions")

    game = Game.query.filter_by(id=game_id).first()
    user = User.query.get_or_404(session['username'])
    form = QuestionForm()

    if form.validate_on_submit():
        question = Question(title=form.title.data,
                        text=form.text.data,
                        game_id=game_id,
                        username=user.username)
        
        db.session.add(question)
        db.session.commit()

        flash('Thanks for your question.  Hopefully it will soon be answered.')
        return redirect(f'/games/{game_id}/questions')

    return render_template('/games/add_question.html', form=form, game=game, user=user)

@app.route('/questions/<question_id>')
def show_question(question_id):
    """Show the selected question"""

    question = Question.query.get_or_404(question_id)
    question = readable_time(question)
    answers = question.answers
    answers = readable_times(answers)
    answers = sorted(answers, key=lambda o: o.id)
    upvotes = []
    if 'username' in session:
        username = session['username']
        user = User.query.get_or_404(username)
        for upvote in user.upvotes:
            if upvote.answer_id:
                upvotes.append(upvote.answer_id)
    return render_template('games/question.html', 
                question=question, game=question.game, upvotes=upvotes, answers=answers)

@app.route('/questions/<question_id>/edit', methods=["GET", "POST"])
def edit_question(question_id):
    """Display form to edit question and handle form submission"""

    question = Question.query.get_or_404(question_id)

    if ('username' not in session) or (session['username'] != question.username):
        flash("Only a question's author can edit a question")
        return redirect(f"/")

    form = QuestionForm(obj=question)

    if form.validate_on_submit():
        if form.title.data:
            question.title = form.title.data
        if form.text.data:
            question.text = form.text.data

        db.session.commit()
        return redirect(f'/questions/{question.id}')

    return render_template('games/edit_question.html', form=form, question=question, game=question.game)

@app.route('/questions/<question_id>/delete', methods=['DELETE'])
def delete_question(question_id):
    """Delete question from database"""

    question = Question.query.get_or_404(question_id)
    game_id = copy.deepcopy(question.game_id)

    if ('username' not in session) or (session['username'] != question.username):
        flash("You can only delete your own question")
        return redirect('/')

    db.session.delete(question)
    db.session.commit()

    resp = {'game_id': game_id}
    return resp


###################### Answer Routes #######################

@app.route('/questions/<question_id>/answer', methods=['POST'])
def post_answer(question_id):
    """Post answer to database and return answer text"""

    if 'username' not in session:
        flash("You must be logged in to answer a question")
        return redirect(f"/")

    text = request.json['text']
    username = session['username']
    question_id = question_id
    answer = Answer(text=text, username=username, question_id=question_id)

    db.session.add(answer)
    db.session.commit()

    resp = {'answer_id': answer.id, 'text': answer.text, 'username': answer.username, 'timestamp': answer.timestamp}

    return resp

@app.route('/answers/<answer_id>/edit', methods=['PATCH'])
def edit_answer(answer_id):
    """Post edit to database and return new text"""

    answer = Answer.query.get_or_404(answer_id)

    if ('username' not in session) or (session['username'] != answer.username):
        flash("You can only edit your own answer", "danger")
        return redirect("/")

    answer.text = request.json['text']

    db.session.commit()

    resp = {'text': answer.text}
    return resp

@app.route('/answers/<answer_id>/delete', methods=['DELETE'])
def delete_answer(answer_id):
    """Delete answer from database"""

    answer = Answer.query.get_or_404(answer_id)

    if ('username' not in session) or (session['username'] != answer.username):
        flash("You can only delete your own answer")
        return redirect('/')

    db.session.delete(answer)
    db.session.commit()

    resp = {'delete': 'success'}
    return resp


################### Upvote Routes ############################

@app.route('/reviews/<review_id>/upvote', methods=["POST"])
def like_review(review_id):
    """Post upvote on review to database"""

    if 'username' not in session:
        flash("You must be logged in to like a review")
        return redirect(f"/")

    review = Review.query.get_or_404(review_id)

    if session['username'] == review.user.username:
        flash("It is important to like yourself, but you can't like your own review")
        return redirect(f"/")

    username = session['username']
    upvote = Upvote(username=username, review_id=review_id)

    db.session.add(upvote)
    db.session.commit()

    resp = {'review': upvote.review_id, 'username': upvote.username}
    return resp

@app.route('/reviews/<review_id>/remove_upvote', methods=["DELETE"])
def unlike_review(review_id):
    """Remove upvote on review from database"""

    if 'username' not in session:
        flash("You must be logged in to remove a like")
        return redirect(f"/")

    review = Review.query.get_or_404(review_id)
    username = session['username']

    for upvote in review.upvotes:
        if upvote.username == username:
            db.session.delete(upvote)
            db.session.commit()
    
    resp = {'review': review.id}
    return resp

@app.route('/answers/<answer_id>/upvote', methods=["POST"])
def like_answer(answer_id):
    """Post upvote on answer to database"""

    if 'username' not in session:
        flash("You must be logged in to like an answer")
        return redirect(f"/")

    answer = Answer.query.get_or_404(answer_id)

    if session['username'] == answer.user.username:
        flash("It is important to like yourself, but you can't like your own answer")
        return redirect(f"/")

    username = session['username']
    upvote = Upvote(username=username, answer_id=answer_id)

    db.session.add(upvote)
    db.session.commit()

    resp = {'answer': upvote.answer_id, 'username': upvote.username}
    return resp

@app.route('/answers/<answer_id>/remove_upvote', methods=["DELETE"])
def unlike_answer(answer_id):
    """Remove upvote on answer from database"""

    if 'username' not in session:
        flash("You must be logged in to remove a like", "danger")
        return redirect(f"/")

    answer = Answer.query.get_or_404(answer_id)
    username = session['username']

    for upvote in answer.upvotes:
        if upvote.username == username:
            db.session.delete(upvote)
            db.session.commit()
    
    resp = {'answer': answer.id}
    return resp