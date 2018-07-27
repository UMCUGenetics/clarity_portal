"""Clarity Portal utility functions."""


class WSGIMiddleware(object):
    """WSGI Middleware."""

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.prefix
        return self.app(environ, start_response)
