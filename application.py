import os, requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from statistics import mean

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("user_id") is None:
        return redirect(url_for("login"))

    return redirect(url_for("search"))

@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id") is not None:
        return redirect(url_for("search"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if the user is registered
        user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password;",
            {"username": username, "password": password}).first()
        
        # if user isn't registered return error page
        if user == None:
            return render_template("error.html", messege="Error: User Not Found")

        # redirect to homepage if login was successful.
        session["user_id"] = user.id
        return redirect(url_for("search"))
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id") is not None:
        return redirect(url_for("search"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password is not None:
            # Insert user info into the database
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password);",
                {"username": username, "password": password})
            
            # commit changes to the database
            db.commit()

            # redirect to the login page after successful registration
            return redirect(url_for("login"))

        # render an error page if registration was unsuccessful
        return render_template("error.html", messege="Error: Couldn't register user, try again.")

    return render_template("signup.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if session.get("user_id") is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        search_query = request.form.get("search-text")

        if search_query == "":
            books = db.execute("SELECT * FROM books;")
        else:
            books = db.execute("SELECT * FROM books WHERE \
                                    isbn LIKE '%{0}%' OR \
                                    title LIKE '%{0}%' OR \
                                    author LIKE '%{0}%';".format(search_query)).fetchall()

        return render_template("search.html", books=books)

    return render_template("search.html")

@app.route("/book/<int:book_id>")
def book(book_id):
    if session.get("user_id") is None:
        return redirect(url_for("index"))
    
    user_id = session.get("user_id")
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).first()
    reviews = db.execute("SELECT review FROM reviews WHERE book_id = :book_id;", {"book_id": book_id}).fetchall()
    good_reads_review = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Pq2ydGCVReVEpYVgC29nJg", "isbns": book.isbn}).json()["books"][0]
    
    if book is None:
        return render_template("error.html", messege="Error: Book Not Found!")

    return render_template("book.html", book=book, reviews=reviews, good_reads_review=good_reads_review)

@app.route("/review/<int:book_id>", methods=["POST"])
def review(book_id):
    if session.get("user_id") is None:
        return redirect(url_for("index"))

    # Get the id of the user rating the movie
    user_id = session.get("user_id")
    rating_score = request.form.get("score")
    review = request.form.get("review")

    if user_id and rating_score and review is not None:
        
        previous_review = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id": user_id, "book_id": book_id}).first()

        if previous_review is not None:
            return render_template("error.html", messege="A user can only rate a book once.")

        db.execute("INSERT INTO reviews (user_id, book_id, rating_score, review) VALUES (:user_id, :book_id, :rating_score, :review)",
                    {"user_id": user_id, "book_id": book_id, "rating_score": rating_score, "review": review})

        # Get all review scores of the book
        reviews = db.execute("SELECT rating_score FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()

        # Calculate the new avg rating score
        avg_reviews = 0.0
        score_sum = 0.0

        for review in reviews:
            score_sum += review["rating_score"]


        avg_reviews = score_sum / len(reviews)
        review_count = len(reviews)

        # update book's avg rating score
        db.execute("UPDATE books SET averege_score = :avg_reviews, review_count = :review_count WHERE id = :book_id", 
                    {"avg_reviews": avg_reviews, "book_id": book_id, "review_count": review_count})
        
        # commit database changes
        db.commit()

        return redirect(url_for("book", book_id=book_id))
    
    return render_template("error.html", messege="Error: Couldn't add review, try again")  

@app.route("/api/<string:isbn>")
def get(isbn):
    # Check if isbn is valid
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).first()
    
    # if book is not in database return error
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 404
    print(book)
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": book.review_count,
        "average_score": float(book.averege_score)
    }), 200