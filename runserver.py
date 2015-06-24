#!/usr/bin/env python

"""
runserver.py
    Run Flask web application on the web server Tornado.

created on 13/June/2014

"""


from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from settings import config
from catalog_app import app


app.secret_key = config.SECRET_KEY
app.debug = True
http_server = HTTPServer(WSGIContainer(app))
http_server.listen(80)
IOLoop.instance().start()

#app.run(host='0.0.0.0', port=8000)
