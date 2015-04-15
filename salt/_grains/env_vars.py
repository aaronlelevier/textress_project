from salt.modules import environ

def env_vars():
    return {'T17_SECRET_KEY': environ.get('T17_SECRET_KEY','')}