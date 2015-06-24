#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/catalog_app/")

from settings import config
from catalog_app import app as application
application.secret_key = config.SECRET_KEY
