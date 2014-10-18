import time
from flask import redirect, url_for, request
from google.appengine.ext import db
from google.appengine.api import users


class NonsensoUsers(db.Model):
    email = db.StringProperty(required=True)
    epoch = db.IntegerProperty(required=True)
    latest = db.IntegerProperty()
    school = db.StringProperty(required=True)

from flask import Flask
app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def index():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.login('/login')
def login():
    user = users.get_current_user()
    if user:
        return app.send_static_file('successfully_logged_in.html')
    return app.send_static_file('login.html')


@app.route('/quiz')
def quiz():
    user = users.get_current_user()
    if not user:
        return redirect(users.create_login_url(request.base_url))
    return 'entered into the quiz'


# 4xx error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return '<h1>Sorry, nothing at this URL.<h1>', 404


@app.errorhandler(401)
def unauthorized(e):
    """ custom 401 error"""
    return '<h1>hey, you there, no wandering around here</h1>', 401
