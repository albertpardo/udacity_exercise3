import os

app_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    DEBUG = True

    # Local Host URL
    HOST = "localhost"
    PORT = 5432
    POSTGRES_URL='{}:{}'.format(HOST, PORT)
    POSTGRES_USER="root" #TODO: Update value
    POSTGRES_PW="root"   #TODO: Update value
    POSTGRES_DB="techconfdb"   #TODO: Update value
    DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or DB_URL
    CONFERENCE_ID = 1
    SECRET_KEY = 'LWd2tzlprdGHCIPHTd4tp5SBFgDszm'
    
    SERVICE_BUS_CONNECTION_STRING ='Endpoint=sb://migrate-app-bus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=NwAP2ykDl9AJkkudcSB/4jnafayABJDy1metMWjM760=' #TODO: Update value
    SERVICE_BUS_QUEUE_NAME ='migratequeue'
    
    ADMIN_EMAIL_ADDRESS = 'albertopardomarti@gmail.com'
    SENDGRID_API_KEY = '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' #Configuration not required, required SendGrid Account

class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False