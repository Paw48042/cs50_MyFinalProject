import os
import re
import datetime
from flask_mail import Mail, Message
from flask_crontab import Crontab
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps


# Make this file a webapp
app = Flask(__name__)

# Config Email
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_DEFAULT_SENDER":os.environ['EMAIL_USER'],
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}
app.config.update(mail_settings)
mail = Mail(app)
crontab = Crontab(app)

# Connect to SQL
db = SQL("sqlite:///project.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    user = session["user_id"]
    query = db.execute("SELECT transaction_id, history.book_id, book_name, date, return_date, status FROM history INNER JOIN book_data ON history.book_id = book_data.book_id WHERE user_id = ?", user)
    return render_template("index.html", query = query)


@app.route("/register", methods=["GET", "POST"])
def register():
    #Do This First
    if request.method == 'POST':
        # Get first name
        first_name = request.form.get('first_name')

        # Get last name
        last_name = request.form.get('last_name')

        # Get the Email
        email = request.form.get('email')

        # Get the Username
        username = request.form.get('username')

        # Get the Password
        password = request.form.get('password')

        # Validate by typing again
        confirmation = request.form.get('confirmation')

        # If bool not null and password is correct hash the pass
        hsh = generate_password_hash(password)
        a = db.execute("SELECT id, username FROM users WHERE username = ?", username)
        que = db.execute("SELECT id FROM users WHERE email = ?", email)
        if not first_name:
            flash("Invalid First Name")
            return redirect("/register")

        elif not last_name:
            flash("Invalid Last Name")
            return redirect("/register")

        elif not email:
            flash("Invalid Email")
            return redirect("/register")

        elif re.search(email, "@") == False:
            flash("Invalid Email")
            return redirect("/register")

        elif bool(que) == True:
            flash("This email have been used")
            return redirect("/register")

        elif not username:
            flash("Invalid Username")
            return redirect("/register")

        elif not password or not confirmation:
            flash("Password Mismatch")
            return redirect("/register")

        elif password != confirmation:
            flash("Password Mismatch")
            return redirect("/register")

        elif bool(a) == True:
            flash("This Username have been used!")
            return redirect("/register")
        else:
            # insert into users table
            db.execute("INSERT INTO users(username, password, firstname, lastname, email, extend_chance) VALUES(?,?,?,?,?,1)", username, hsh, first_name, last_name, email)

            flash("Check your Confirmation Email (sometimes in spam section)")
            content = "Hi and Welcome, This is just a Confirmation Email, if you recieves this email that's mean you successfully registered our app!"
            msg = Message(subject = "Thank you, You have sucessfully registered shared!" , body = content, recipients=[email])
            mail.send(msg)
            return redirect("/login")
    return render_template('register.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Incorrect username or password")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Incorrect username or password")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("Incorrect username or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        # Get Username
        username = request.form.get("username")

        # Get Email
        email = request.form.get("email")

        # Query to find if the Username and email is valid
        query = db.execute("SELECT * FROM users WHERE username = ? AND email = ?", username, email)

        if not username:
            flash("Username is Missing")
            return redirect("/")
        elif not email:
            flash("Email is Missing")
            return redirect("/")
        elif query is None:
            flash("Incorrect Username")
            return redirect("/")
        else:
            password = check_password_hash(db.execute("SELECT password FROM users WHERE username = ?", username)[0]["password"])
            msg = Message("Your Password is: {}".format(password), recipients = [email])
            mail.send(msg)
            return redirect("/login")
    return render_template("forgot.html")

# register login logout forget password is finish

# To do function is 1. index page 2. borrow / borrowed page 3. extend page 4. Make a Notification when it's time to return


@app.route("/lookup" , methods=["GET","POST"])
@login_required
def lookup():
    if request.method == "POST":
        search = request.form.get("search")
        clue = request.form.get("clue")
        if not search or not clue:
            query = db.execute("SELECT * FROM book_data")
            return render_template("found.html", query = query)
        elif search == 'Book_ID':
            if bool(re.search("[a-zA-Z]",clue)) == True:
                flash("Only numbers")
                return render_template("lookup.html")
            query = db.execute("SELECT * FROM book_data WHERE book_id = ?", clue)
            return render_template("found.html", query = query)

        elif search == 'Book_Name':
            query = db.execute("SELECT * FROM book_data WHERE book_name like ?", "%" + clue + "%")
            return render_template("found.html", query = query)

        elif search == 'Release_Year':
            query = db.execute("SELECT * FROM book_data WHERE release_year = ?", clue)
            return render_template("found.html", query = query)
        elif clue == "all":
            query = db.execute("SELECT * FROM book_data")
            return render_template("found.html", query = query)

    return render_template("lookup.html")

@app.route("/borrow" , methods = ["GET","POST"])
@login_required
def borrow():
    user = session["user_id"]
    email = db.execute("SELECT email FROM users WHERE id = ?", user)[0]['email']
    if "books" not in session:
        session["books"] = []
    if request.method == "POST":
        search = request.form.get("search")
        clue = request.form.get("clue")
        if not search or not clue:
            try:
                borrows = request.form.get("borrow")
                db.execute("INSERT INTO history (book_id, user_id, date, return_date) VALUES (?, ?, datetime('now'), datetime('now', '+7 day'))", borrows , user)
                db.execute("UPDATE book_data SET status = 'Borrowed' WHERE book_id = ?", borrows)
                flash("You've successfully borrow book")
                # send email as a ticket to receives the book by yourselves
                content = "You can come and pickup Your book at 1-29 INF-BN Headquarter at anytime. Borrow duration is 7 days, Please return the book before that, or you maybe charge 20 Baht for that."
                msg = Message(subject = "Your book is ready" , body = content, recipients=[email])
                mail.send(msg)
                return redirect("/")
            except:
                flash("Error, Not Found")
                return redirect("/borrow")
        elif search == 'Book_ID':
            if bool(re.search("[a-zA-Z]",clue)) == True:
                flash("Only numbers")
                return render_template("borrow.html")
            query = db.execute("SELECT * FROM book_data WHERE book_id = ?", clue)
            return render_template("borrow.html", query = query)

        elif search == 'Book_Name':
            query = db.execute("SELECT * FROM book_data WHERE book_name like ?", "%" + clue + "%")
            return render_template("borrow.html", query = query)

        elif search == 'Release_Year':
            query = db.execute("SELECT * FROM book_data WHERE release_year = ?", clue)
            return render_template("borrow.html", query = query)

        elif clue == "all":
            query = db.execute("SELECT * FROM book_data")
            return render_template("borrow.html", query = query)

    return render_template("borrow.html")


@app.route("/extend", methods = ["GET","POST"])
@login_required
def extended():
    user = session["user_id"]
    # Make a table show what book you've borrow and still haven't return
    query = db.execute("SELECT history.book_id, book_name, date, return_date, status FROM history INNER JOIN book_data ON history.book_id = book_data.book_id WHERE user_id = ?", user)

    # You can click on extend button to extend the duration for another 14 days from the day you click the button
    if request.method == "POST":
        # make a query for update status
        extend = request.form.get("extend")
        chance = db.execute("SELECT extend_chance FROM users WHERE id = ?", user)[0]['extend_chance']
        if chance >= 1:
            db.execute("UPDATE book_data SET status = 'Extended' WHERE book_id = ?", extend)
            db.execute("UPDATE history SET return_date = datetime(return_date, '+7 day') WHERE book_id = ? AND user_id = ?", extend, user)
            db.execute("UPDATE users SET extend_chance = extend_chance - 1 WHERE id = ?", user)
            flash("You've successfully extend your borrowing time")
            return redirect("/")
        else:
            flash("You've used up all your extend chance, Please return the book first to get your extend chance back")
            return redirect("extend")

    return render_template("extend.html", query = query)
