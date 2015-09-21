from .base import *


SITE_URL = "http://localhost:8000"

if 'test' in sys.argv:
    from .test import *