import os
import pathlib
import string
import pandas as pd

from flask import Flask, request, jsonify, render_template, redirect, session, abort, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from linkedin_api import Linkedin
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

client = MongoClient("mongodb+srv://MrAlumni:iitisoc123@alumniportal.g0c22w7.mongodb.net/")

# Select the "Alumni" database
dab = client["Alumni"]

# Select the "Data" collection
data_collection = dab["Data"]
messages_collection = dab["messages"]
MAILS = dab.Mails
FORUMS = dab.Forums

app = Flask("Google Login App")
app.secret_key = "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"

socketio = SocketIO(app, message_queue="redis://localhost:6379/")
app.config["SECRET_KEY"] = "80085"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "886588755390-1spe51df9k9uiimti149uf716fdujake.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:5000/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


def login_required_routes(route_list):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if "google_id" not in session:
                return redirect(url_for("login"))
            else:
                return function(*args, **kwargs)

        wrapper.__name__ = function.__name__
        if hasattr(function, "_rule"):
            route_list.append(function._rule)
        return wrapper

    return decorator


# List of routes that require login (add all the routes except "home", "login", and "home2")
login_required_routes_list = ["/protected_area", "/room", "/get_profile", "/profile", "/chat", "/linkedinurl"]


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    # Example code for increasing clock skew tolerance to 5 minutes (300 seconds)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=10  # 5 minutes tolerance
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")

    existing_profile = data_collection.find_one({"email": session['email']})
    if existing_profile:
        return redirect(url_for('profile', **existing_profile))

    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/log")
def log():
    return render_template('login.html')


@app.route("/")
def home():
    return render_template('compiled.html')


@app.route("/home")
def home2():
    return render_template('compiled.html')


@app.route('/jobs')
@login_required_routes(login_required_routes_list)
def jobs():
    return render_template('jobs.html')


@app.route('/events')
def events():
    return render_template('events.html')


@app.route("/protected_area")
@login_required_routes(login_required_routes_list)
def protected_area():
    existing_profile = data_collection.find_one({"email": session['email']})
    if existing_profile:
        return redirect(url_for('profile', **existing_profile))

    if session['email'].split('@')[1] == 'alum.iiti.ac.in' or session['email'] in ('cse220001078@iiti.ac.in', 'mralumniportal@gmail.com'):
        return render_template('linkedinurl.html')
    else:
        session.clear()

        # Revoke the access token
        access_token = request.cookies.get("access_token")  # Assuming you are storing the access token in a cookie
        if access_token:
            revoke_token(access_token)
        return "Unauthorised Login. Only an official institute Alumni ID can login."


def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route("/chat", methods=["POST", "GET"])
@login_required_routes(login_required_routes_list)
def chat():
    if request.method == "POST":
        name = session['name']
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("chat.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("chat.html", error="Please enter a room code.", code=code, name=name)

        room = code
        if create != False:
            room = generate_unique_code(4)

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("chat.html")


@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None:
        return redirect(url_for("chat"))

    return render_template("room.html", code=room, messages=messages_collection.find({"_id": session.get("room")}, {"_id": 0}))


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room is None:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    messages_collection.insert_one(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on("connect")
def connect():
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


@app.route('/linkedinurl', methods=['GET'])
@login_required_routes(login_required_routes_list)
def linkedinurl():
    existing_profile = data_collection.find_one({"email": session['email']})
    if existing_profile:
        return redirect(url_for('profile', **existing_profile))
    return render_template('linkedinurl.html')


@app.route('/get_profile', methods=['POST'])
@login_required_routes(login_required_routes_list)
def get_profile():
    # Authenticate using any LinkedIn account credentials
    api = Linkedin('mralumniportal@gmail.com', 'iitisoc123')

    if session['email'][0:2] == 'ee':
        branch = 'Electrical'

    if session['email'][0:4] != 'mems' and session['email'][0:2] == 'me':
        branch = 'Metallurgical'

    if session['email'][0:4] == 'mems':
        branch = 'Mechanical'

    if session['email'][0:2] == 'ce':
        branch = 'Civil'

    else:
        branch = 'Computer Science'

    # Retrieve the profile URL from the request
    profile_url = request.form['profile_url']

    urli = profile_url

    # Parse the profile URL to extract the profile identifier
    profile_id = profile_url.split('/')[-2]

    if len(profile_id) <= 1:
        profile_id = profile_url.split('/')[-1]

    # Get the member's profile
    profile = api.get_profile(profile_id)

    profile_picture_url = profile.get("pictureUrls", [""])[0]
    session["profile_picture_url"] = profile_picture_url

    # Extract the information
    location_name = profile.get('locationName')
    first_name = profile.get('firstName')
    last_name = profile.get('lastName')
    headline = profile.get('headline')

    if headline == None:
        return redirect('/protected-area')
    else:
        experiences = profile.get('experience', [])
        companies = []
        headlines = []

        for exp in experiences:
            company = exp.get('companyName')
            if company:
                companies.append(company)

            position = exp.get('title')
            if position:
                headlines.append(position)

        # Create a dictionary with the extracted information
        extracted_info = {
            "location_name": location_name,
            "first_name": first_name,
            "last_name": last_name,
            "headline": headline,
            "companies": companies,
            "headlines": headlines,
            "url": urli,
            "branch": branch,
            "email": session['email'],
            "name": session['name'],
            "profile_picture_url": session.get("profile_picture_url", "")
        }

        # Check for duplicate profile in MongoDB collection
        existing_profile = data_collection.find_one({"email": session['email']})

        if existing_profile:
            return redirect(url_for('profile', **existing_profile))

        # Store the profile information in MongoDB if not a duplicate
        try:
            data_collection.insert_one(extracted_info)
            return redirect(url_for('profile', **extracted_info))
        except DuplicateKeyError:
            return redirect('/protected_area')


def load_profiles_from_excel(excel_file):
    # Load the existing profiles from the Excel file into a DataFrame
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, engine="openpyxl")
    else:
        df = pd.DataFrame()

    # Drop duplicate profiles based on specific columns (location_name, first_name, last_name, and headline)
    df = df.drop_duplicates(
        subset=["location_name", "first_name", "last_name", "headline"])

    return df


def profile_exists(profiles_collection, extracted_info):
    # Check if the profile already exists in the MongoDB collection based on specific columns
    existing_profile = profiles_collection.find_one({
        "location_name": extracted_info["location_name"],
        "first_name": extracted_info["first_name"],
        "last_name": extracted_info["last_name"],
        "headline": extracted_info["headline"]
    })

    return existing_profile is not None


@app.route('/profile', methods=['GET'])
@login_required_routes(login_required_routes_list)
def profile():
    extracted_info = {
        "location_name": request.args.get('location_name'),
        "first_name": session['name'],
        "last_name": '',
        "headline": request.args.get('headline'),
        "companies": request.args.getlist('companies'),
        "headlines": request.args.getlist('headlines'),
        "url": request.args.get('url'),
        "branch": request.args.get('branch'),
        "email": request.args.get('email')
    }
    excel_file = "profile_info.xlsx"
    df = load_profiles_from_excel(excel_file)

    df = pd.concat([df, pd.DataFrame([extracted_info])], ignore_index=True)

    df.to_excel(excel_file, index=False, engine="openpyxl")

    return render_template('profile.html', extracted_info=extracted_info)


@app.route('/profiles', methods=['GET'])
@login_is_required
def profiles():
    all_profiles = list(data_collection.find())

    return render_template('profiles.html', all_profiles=all_profiles)


@app.route('/searchprofile', methods=['GET', 'POST'])
@login_required_routes(login_required_routes_list)
def searchprofile():
    if request.method == 'POST':
        email = request.form.get('email')

        profile = data_collection.find_one({"email": email})

        if profile:
            return render_template('individualprofile.html', extracted_info=profile)
        else:
            error_message = f"No profile found for the email: {email}"
            return render_template('searchprofile.html', error=error_message)

    return render_template('searchprofile.html')


if __name__ == "__main__":
    app.run(debug=True)
    socketio.run(app, port=5000, debug=True)
