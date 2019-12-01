from flask import Flask
import os
from dotenv import load_dotenv
load_dotenv()

application = Flask(__name__)
application.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
application.config['DYNAMODB_TABLE'] = os.getenv('DYNAMODB_TABLE_NAME')
application.config['DYNAMODB_REGION'] = os.getenv('DYNAMODB_REGION_NAME')
application.config['DYNAMODB_KEY'] = os.environ.get("AWS_ACCESS_KEY_ID")
application.config['DYNAMODB_SECRET'] = os.environ.get("AWS_SECRET_ACCESS_KEY")
application.config['LOGIN_EMAIL'] = os.environ.get("EMAIL")
application.config['LOGIN_PASSWORD'] = os.environ.get("PASSWORD")
application.config['HTTP_SSL'] = os.environ.get("HTTP")

from my_app import routes

if __name__ == '__main__':
    #app.run()# for Heroku
    application.run(debug=True)# for development  


