#!/usr/bin/env python

"""auth.py
This module handles requests and responses of
        authenticate and authorize users.
Attributes:
    auth: Flask blueprint instance which bind /auth url

Functions:
    login(cached_email=None):
    signup()
    gconnect()
    gdisconnect()
    fconnect()
    logout()

created on 13/June/2014
"""


import json

import httplib2
import re
import requests

from flask import render_template, request, Blueprint, \
    redirect, url_for, flash, make_response
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from catalog_app import session
from catalog_app.api.models import User
from util import check_password, encrypt_password, \
    generate_token, generate_csrf_token
from settings import config


# Client_ID for Google + login.
# Please make sure that you have downloaded and placed
#     client_secret.json properly. Please read README file.
CLIENT_ID = json.loads(
    open('settings/client_secret.json', 'r').read())['web']['client_id']

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login/', methods=['GET', 'POST'])
def login(cached_email=None):
    """Render login page and handle login form data.
        Requests:
            GET /auth/login
            POST /auth/login
    """
    if request.method == 'GET':
        csrf_token = generate_csrf_token()
        response = make_response(
            render_template('login.html', cached_email=cached_email,
                            client_id=CLIENT_ID, csrf_token=csrf_token)
        )
        # Store the csrf_token in the browser cookie.
        response.set_cookie('csrf_token', value=csrf_token)
        return response

    # Form fields:
    #     email: user email, required
    #     password: user password, required
    if request.method == 'POST':
        # Check csrf token
        cookie_csrf_token = request.cookies.get('csrf_token')
        form_csrf_token = request.form.get('_csrf_token')

        # CSRF attack detected!
        if cookie_csrf_token != form_csrf_token:
            flash("Please use proper login.")
            return render_template('login.html', cached_email=cached_email,
                                   client_id=CLIENT_ID, csrf_token="")

        # Get user data from login form.
        email = request.form.get('email')
        password = request.form.get('password')

        # User must fill the email and password field.
        if not (email and password):
            flash("Please fill the form. ")
            return render_template('login.html', cached_email=email)

        # Find user in the database by email.
        user = User.get_by_email(session, email.strip())
        # User does not exists.
        if not user:
            flash("Invalid email address or password. ")
            return render_template('login.html', cached_email=email)

        # User exist, but Password does not.
        # The user have logged in with OAuth
        if not user.password:
            flash("You've signed up with social service. ")
            return render_template('login.html', cached_email=email)

        # Password incorrect.
        if not check_password(password, user.password, user.salt):
            flash("Invalid email address or password. ")
            return render_template('login.html', cached_email=email)

        # Generate JSON web token for user.
        # As long as client has non-expired and valid token,
        #     they do not need to login again.
        expire_time, token = generate_token(user)
        response = make_response(redirect(url_for('basic.showMain')))
        # Store the token in the browser cookie.
        response.set_cookie('token', value=token)
        response.set_cookie('expire_time', value=str(expire_time))
        return response


@auth.route('/signup/', methods=['GET', 'POST'])
def signup():
    """Render login page and handle login form data.
        Requests:
            GET /auth/signup
            POST /auth/signup
    """
    if request.method == 'GET':
        csrf_token = generate_csrf_token()
        response = make_response(
            render_template('signup.html', client_id=CLIENT_ID)
        )
        # Store the csrf_token in the browser cookie.
        response.set_cookie('csrf_token', value=csrf_token)
        return response

    # Form fields:
    #     email: user email, required
    #     password: user password, required
    #     confirm: user confirm password, required
    # User email, and hashed password and salt are stored when login succeed.
    if request.method == 'POST':
        # Check csrf token
        cookie_csrf_token = request.cookies.get('csrf_token')
        form_csrf_token = request.form.get('_csrf_token')

        # CSRF attack detected!
        if cookie_csrf_token != form_csrf_token:
            flash("Please use proper signup.")
            return render_template('signup.html',
                                   client_id=CLIENT_ID, csrf_token="")

        # Get user data from login form.
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        # User must fill the email and password field.
        if not (email and password and confirm):
            flash("Please fill the form. ")
            return render_template('signup.html', cached_email=email)

        # Password field and confirm fields must be the same.
        if not (password == confirm):
            flash("Confirm password has to be the same as password")
            return render_template('signup.html', cached_email=email)

        # Find user in the database by email.
        user = User.get_by_email(session, email.strip())
        # User already exist, remind user that.
        if user:
            if user.password:
                flash("Such user already exist. Please login")
                return render_template('signup.html', cached_email=email)
        # Create a new user object
        else:
            user = User(email=email.strip())
        # Store encrypted password and salt in the database
        user.password, user.salt = encrypt_password(password)
        session.add(user)
        session.commit()

        # Generate JSON web token for user.
        # As long as client has non-expired and valid token,
        #     they do not need to login again.
        expire_time, token = generate_token(user)
        response = make_response(redirect(url_for('basic.showMain')))
        # Store the token in the browser cookie.
        response.set_cookie('token', value=token)
        response.set_cookie('expire_time', value=str(expire_time))
        return response


@auth.route('/gconnect/', methods=['POST'])
def gconnect():
    """Handle Google OAuth login.
        GET /auth/gconnect
        If user does not exists create a new user.
    """

    # Check csrf token
    cookie_csrf_token = request.cookies.get('csrf_token')
    if request.args.get('_csrf_token') != cookie_csrf_token:
        flash("Please use proper authentication.")
        response = make_response(json.dumps('Fail to connect'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # code is a return value from front-end google + oauth API
    code = request.data
    try:
        # Create oauth login flow based on client_secret.json
        # Please make sure that you have downloaded and placed
        #     client_secret.json properly. Please read README file.
        oauth_flow = flow_from_clientsecrets('settings/client_secret.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        flash("Google plus connection Error.")
        response = make_response(json.dumps('Fail to upgrade'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Get an access_token from Goolge OAuth provider
    access_token = credentials.access_token
    url = ('https://www.googleapis.'
           'com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        flash("Google plus connection Error.")
        response = make_response(
            json.dumps(result.get('error')), 500
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get user id stored in Google
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        flash("Google plus connection Error.")
        response = make_response(
            json.dumps("Token's user ID doesn't match"), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Make sure client id is correct
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID doesn't match"), 401
        )
        flash("Google plus connection Error.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Retrieve user info. stored in Google
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = json.loads(answer.text)
    email = data['email']
    user = User.get_by_email(session, email.strip())

    # If user does not exist, create a new user
    if not user:
        user = User(email=email)

    session.add(user)
    session.commit()

    # Generate JSON web token for user.
    # As long as client has non-expired and valid token,
    #     they do not need to login again.
    flash("Successfully logged in with Google +")
    expire_time, token = generate_token(user)
    response = make_response(redirect(url_for('basic.showMain')))
    # Store the JSON web token and Google + access token in the browser cookie.
    response.set_cookie('token', value=token)
    response.set_cookie('expire_time', value=str(expire_time))
    response.set_cookie('gplus_token', value=access_token)
    return response


@auth.route('/gdisconnect', methods=['GET'])
def gdisconnect():
    """Handle Google OAuth disconnect.
        GET /auth/gdisconnect
    """
    # Get Google + access token from cookie.
    access_token = request.cookies.get('gplus_token')
    # User already logged out, if there is no token.
    if access_token is None:
        response = make_response(
            json.dumps('Current user is not connected.'), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Request to disconnect.
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # The user is successfully disconnected.
    if result['status'] == '200':
        response = make_response(
            json.dumps('Successfully disconnected'), 200
        )
        response.set_cookie('gplus_token', '', expires=0)
        response.headers['Content-Type'] = 'application/json'
        return response
    # The user is failed to disconnected.
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user'), 400
        )
        response.headers['Content-Type'] = 'application/json'
        return response


@auth.route('/fconnect/', methods=['POST'])
def fconnect():
    """Handle facebook OAuth login
        GET /auth/fconnect
        If user does not exists create a new user.
    """
    # userinfo has email, username, and access token
    userinfo = json.loads(request.data)
    user_access_token = userinfo.get('access_token')

    # To verify user's access token, we need to get our app token first.
    url = ('https://graph.facebook.com/oauth/access_token?'
           'client_id={}&client_secret={}'
           '&grant_type=client_credentials'
           .format(config.FACEBOOK_CLIENT_ID,
                   config.FACEBOOK_CLIENT_SECRET))
    try:
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        app_token = re.search(r'(access_token=)(.+?$)', result).group(2)

        print app_token

        # Using app token, we can verify user's access token
        url = ('https://graph.facebook.com/debug_token'
               '?input_token={}&access_token={}'
               .format(user_access_token, app_token))

        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        user_data = result.get("data")

        # If the user's token is valid to the app token,
        # Facecook api returns the variable 'is_valid' with True
        if not user_data.get("is_valid"):
            response = make_response(
                json.dumps("User access token is not valid"), 401
            )
            flash("Facebook connection Error.")
            response.headers['Content-Type'] = 'application/json'
            return response

        email = userinfo.get('email')
        user = User.get_by_email(session, email.strip())

        # Create and store a new user if there is no user exist
        if not user:
            user = User(email=email)
            session.add(user)
            session.commit()

        expire_time, token = generate_token(user)
        flash("Successfully logged in with Facebook")
        response = make_response(
            redirect(url_for('basic.showMain')), 200
        )
        response.set_cookie('token', value=token)
        response.set_cookie('expire_time', value=str(expire_time))
        return response
    except:
        response = make_response(
            json.dumps("User access token is not valid"), 401
        )
        flash("Facebook connection Error.")
        response.headers['Content-Type'] = 'application/json'
        return response


@auth.route('/logout/')
def logout():
    """Handle user logout event.
    """
    token = request.cookies.get('token')
    response = make_response(
        json.dumps("Successfully logged out"), 200
    )
    if not token:
        response = make_response(
            json.dumps("You've already logged out"), 200
        )

    flash("Successfully logged out.")
    # Delete JSON web token.
    response.set_cookie('token', '', expires=0)
    # Make token expired.
    response.set_cookie('expire_time', '', expires=0)
    return response
