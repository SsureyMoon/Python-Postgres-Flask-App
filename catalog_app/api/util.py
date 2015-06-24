"""util.py
This module contains helper functions.

Functions:
    encrypt_password(password)
    check_password(password, encrypted_password, salt)
    generate_token(user)
    validate_token(token, expire_time)

created on 13/June/2014
"""


import string
import random
import time
import uuid
import hashlib
import jwt

import settings.config


def encrypt_password(password):
    """
    Get plain password
    Return encrypted password and salt
    :param password:
    :return encrypted_password, salt:
    """
    salt = uuid.uuid4().hex
    encrypted_password = hashlib.sha256(password.encode('utf-8') + salt)\
        .hexdigest()
    return encrypted_password, salt


def check_password(password, encrypted_password, salt):
    """
    Get user inputted password
    Return True/False whether the password is valid or not
    :param password:
    :param encrypted_password:
    :param salt:
    :return:
    """
    return encrypted_password ==\
        hashlib.sha256(password.encode('utf-8') + salt).hexdigest()


def generate_token(user):
    """
    Generate JSON web token corresponding to the user data
    HMAC SHA256 algorithm is used.
    :param user:
    :return:
    """
    header = {
        "type": "JWT",
        "hash": "SHA256"
    }
    # Token will be expired in an hour: 3600 seconds.
    expire_time = int(time.time()) + 3600
    payload = {
        'exp': expire_time,
        'username': user.name,
        'id': user.id
    }
    # Please make sure that you set proper secret key for your app.
    secret = settings.config.SECRET_KEY
    # We use HMAC-SHA256 algorithm for the signature of the token.
    signature = jwt.encode(payload=payload, key=secret,
                           algorithm='HS256', headers=header)
    return expire_time, signature


def validate_token(token, expire_time):
    """
    Get JSON web token,
    Return False if the token is not valid,
        or user data in the token if it is valid.
    :param token:
    :param expire_time:
    :return:
    """
    if int(time.time()) > int(expire_time):
        # token expired
        return False
    secret = settings.config.SECRET_KEY
    try:
        result = jwt.decode(jwt=token, key=secret, algorithms='HS256')
        return result
    except:
        return False


def generate_csrf_token():
    token = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    return token
