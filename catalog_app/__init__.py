"""
This module instantiates properties,
so other Flask modules can use them.
It also registers blue prints

Attributes:
    engine: object of database engine
    session: accessible database session
    app: Flask app, Tornado can run this app. See also: runserver.py
"""

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_app.api.models import Base

from settings import config


engine = create_engine(
    config.DATABASE_URI
)

Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Blueprint
# These modules have to be imported here, not at top of file.
from catalog_app.api.auth import auth
from catalog_app.api.controllers import basic


# Initialize Flask Application
# Register two blueprints which implements two modules:
# basic: / and its' sub urls
# auth: /auth and its' sub urls
app = Flask(__name__)
app.register_blueprint(basic)
app.register_blueprint(auth)
