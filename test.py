'''
test.py
=======

Use:

    Can run from command line to text ``uwsgi`` with ``nginx-rproxy`` 
    without involving the database, any env var's, etc...

Example command:

    ``uwsgi --socket :8001 --wsgi-file test.py``

'''


def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello World"] # python3
    #return ["Hello World"] # python2