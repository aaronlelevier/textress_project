from salt.modules import environ

def env_vars():
    return {
        'T17_SECRET_KEY': environ.get('T17_SECRET_KEY',''),
        'T17_MANDRILL_API_KEY': environ.get('T17_MANDRILL_API_KEY',''),
        'T17_PHONE_NUMBER': environ.get('T17_PHONE_NUMBER',''),
        'T17_DB_NAME': environ.get('T17_DB_NAME',''),
        'T17_DB_USER': environ.get('T17_DB_USER',''),
        'T17_DB_PASSWORD': environ.get('T17_DB_PASSWORD','')
    }
