import os

app_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    DEBUG = True

    # Local Host URL
    HOST = "migrate-app-server.postgres.database.azure.com"
    PORT = 5432
    POSTGRES_URL='{}:{}'.format(HOST, PORT)
    POSTGRES_USER="azureuser@migrate-app-server" #TODO: Update value
    POSTGRES_PW="myPassword1"   #TODO: Update value
    POSTGRES_DB="techconfdb"   #TODO: Update value
    DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or DB_URL
    CONFERENCE_ID = 1
    SECRET_KEY = 'LWd2tzlprdGHCIPHTd4tp5SBFgDszm'
    
    SERVICE_BUS_CONNECTION_STRING ='Endpoint=sb://migrate-app-bus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=Od2KWfJZf9e3f+I47mNXYh6MQixRt3Sgow2m5xeUO2c=' #TODO: Update value
    SERVICE_BUS_QUEUE_NAME ='notificationqueue'
    
    ADMIN_EMAIL_ADDRESS = 'albertopardomarti@gmail.com'
    SENDGRID_API_KEY = '--NONE--' #Configuration not required, required SendGrid Account

class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False