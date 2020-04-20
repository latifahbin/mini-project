# Import Libraries
from flask import Flask, render_template, request, jsonify, json, url_for, abort, redirect, session, flash
import requests
from cassandra.cluster import Cluster
# from cassandra.cqlengine import connection
from flask_sqlalchemy import sqlalchemy, SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# Config file for API key
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config-keys')
app.config.from_pyfile('config-keys.py')
API_KEY = app.config['API_KEY']

cluster = Cluster()
session_C = cluster.connect('app_weather')

""" the name of the database """
db_name = "auth.db"

""" seesion requires SECRET_KEY, flash and Flask Sqlalchemy to work """
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{db}'.format(db=db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = '{Your Secret Key}'

db = SQLAlchemy(app)


class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    pass_hash = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '' % self.username

# To create new db in current directory, Execute the following lines first time


def create_db():
    """ # Execute this first time to create new db in current directory. """
    db.create_all()


"""
the folllowing function to implement signup, which works as following:
1. Allows username and password for new user.
2. Username and password are required else raises sqlalchemy.exc.IntegrityError.
3. Hashes password with salt using werkzeug.security.
4. Stores username and hashed password inside database.
5. Username should to be unique else raises sqlalchemy.exc.IntegrityError.
"""


@app.route("/signup/", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if not (username and password):
            flash("Username or Password cannot be empty")
            return redirect(url_for('signup'))
        else:
            username = username.strip()
            password = password.strip()

        """ Returns salted pwd hash in format : method$salt$hashedvalue"""
        hashed_pwd = generate_password_hash(password, 'sha256')

        new_user = User(username=username, pass_hash=hashed_pwd)
        db.session.add(new_user)
        flash("user has beed added")

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash("Username {u} is not available.".format(u=username))
            return redirect(url_for('signup'))

        flash("User account has been created.")
        return redirect(url_for("login"))

    return render_template("signup.html")


"""the folllowing function to implement login, which works as following:
1. Uses form to get username and password from the users
2. finds the username in the db for given input
3. Checks password hashed from db for given input username and password.
4. If the password matches redirects validated users to home page/Username
5.  else redirect to login page with error message.
"""
@app.route("/", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if not (username and password):
            flash("Username or Password cannot be empty")
            return redirect(url_for('login'))
        else:
            username = username.strip()
            password = password.strip()

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.pass_hash, password):
            session[username] = True
            return redirect(url_for("user_home", username=username))
        else:
            flash("Invalid username or password.")

    return render_template("login_form.html")

    """
    Home page for  authorized user .
    """


@app.route("/user/<username>/")
def user_home(username):
    return render_template("user_home.html", username=username, )


"""The following function to logout and redirect the user to login page.."""
@app.route("/logout/<username>")
def logout(username):
    session.pop(username, None)
    flash("You have logged out from " + username + " successfully ")
    return redirect(url_for('login'))


# URL for the API
url_weather = 'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}'
# my_url = 'http://api.apixu.com/v1/current.json?key={API_KEY}&q={location}'

""" the following function works as follow:
1. Gets the temperatures from the API (api.openweathermap.org)
2. Converts the temperatures from Kelvin to Celsius
3. returns the temperatures """


def temp(city_name):
    url_full = url_weather.format(API_KEY=API_KEY, city_name=city_name)
    resp = requests.get(url_full)
    json_object = resp.json()
    temp_k = float(json_object['main']['temp'])
    temp_c = temp_k - 273.15
    temp_max = float(json_object['main']['temp_max'])
    temp_max_c = temp_max - 273.15
    temp_min = float(json_object['main']['temp_min'])
    temp_min_c = temp_min - 273.15
    Humidity = float(json_object['main']['humidity'])
    feel = float(json_object['main']['feels_like'])
    feel_c = feel - 273.15
    return temp_c, temp_max_c, temp_min_c, Humidity, feel_c

# Show result as user request
@app.route('/result', methods=['POST', 'GET'])
def my_form_post():
    city_name = request.form['text']
    temp_c, temp_max_c, temp_min_c, Humidity, feel_c = temp(city_name)

    return render_template("result.html", city=city_name, temp=temp_c, temp_min=temp_min_c, temp_max=temp_max_c, temp_feel=feel_c, hum=Humidity)


"""The follwing function works as follow:
1. Gets the validated Username
2. searchs in cassandra database for the user list (list of cities)
3. returns json file which includes (username, cities name)"""


@app.route("/my_list/<username>", methods=['POST', 'GET'])
def my_list(username):
    username = username[:-1]

    rows = session_C.execute(
        """select * from user_list where username= '{}'""".format(str(username)))
    result = []
    for row in rows:
        result.append({"user name": row.username, "City name": row.city_name})

    return jsonify(result)


"""The follwing function works as follow:
1. Gets the validated Username
2. searchs in cassandra database for the user list (list of cities)
3. Goes through for loop:
    I. calls the API for each city
    II. save the result in (responses)

4. returns the responses file which includes the cities' temperatures"""


@app.route("/temperatures/<username>", methods=['GET', 'POST'])
def temperatures(username):
    username = username[:-1]
    rows = session_C.execute(
        """select * from user_list where username= '{}'""".format(str(username)))
    result = []
    responses = []
    for row in rows:
        result.append({"user name": row.username, "City name": row.city_name})
        url_full = url_weather.format(API_KEY=API_KEY, city_name=row.city_name)
        resp = requests.get(url_full)
        data = json.loads(resp.text)
        responses.append(data)
    return jsonify(responses)

# Implements edit functionality. Allows the user to edit his/her list, by add new city to the list
@app.route("/edit_mylist/<username>", methods=['POST'])
def edit_mylist(username):
    city_name = request.form['text'].lower()
    username = username.lower()
    session_C.execute(
        "insert into user_list (username,city_name) values ('{}','{}')".format(username, city_name))
    flash("The city has been added to your list")
    return render_template("user_home.html", username=username)

# Implements delete functionality. Allows the user to delete from his/her list
@app.route("/delete_mylist/<username>", methods=['POST'])
def delete_mylist(username):
    username = username.lower()
    city_name = request.form['text'].lower()
    session_C.execute(
        "delete from user_list where username='{}' and city_name='{}'".format(username, city_name))
    flash("The city has been deleted from your list")
    return render_template("user_home.html", username=username)


# Run program
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
