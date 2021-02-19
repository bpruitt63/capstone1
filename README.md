# capstone1
Springboard Capstone Project 1  
Gamey-Project  
https://gamey-project.herokuapp.com/   

This is a website for video game information.  You can search any game and find basic game info, screenshots, and user written reviews.  Users can also ask questions that can be answered by other users.

Features include the ability to create and view a user profile (allowing controlled submission of content and the ability to view who is creating content), the ability to write a review, which other users can then upvote to make it known if a review is particularly well written, and the ability to ask and answer questions.  Answers to questions can also be upvoted in order to show if they are helpful and accurate.

Standard user flow:  Unregistered users can view all content, but cannot write reviews, questions, answers, or provide upvotes.  Users can also login from a link available on every page, or register a new account from a link on every page on large screens, or on the login page on small screens.  User profile is available from all screens, allowing registered users to edit their profile or logout.  The search bar is available from any page on the website, allowing anyone to search for games.  Searching will return a list of games similar to the search terms.  Clicking on the game link will bring you to the game info page, which also includes links to the game's screenshots, as well as the game's reviews and questions pages.  From those pages, logged in users can submit a review or a question, or follow links to previously submitted reviews or questions.  From a specific review's page, users can upvote a review.  From a specific question's page, users can answer the question, as well as upvote answers that were submitted by other users. 

API = https://rawg-video-games-database.p.rapidapi.com/games  
API terms require a link to API on every page where API is accessed.  To simplify and to give the API as much exposure as possible, the link is just in the footer of every page regardless of whether or not the API is used on that page.

Project deployed on Heroku, created using Flask with Python, Jinja, Flask SQLAlchemy, Flask WTForms, Flask Bcrypt.  Javascript with axios used on a few pages.