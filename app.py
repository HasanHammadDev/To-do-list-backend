from flask import Flask, redirect, url_for, render_template, request
from models import db
from blueprints.database import database_bp
from blueprints.register import register_bp
from blueprints.login import login_bp
from blueprints.todos import todos_bp
from blueprints.logout import logout_bp
from flask_cors import CORS
from flask_migrate import Migrate
import os


# Flask
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = True
migrate = Migrate(app, db)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

app.register_blueprint(database_bp, url_prefix='/database')
app.register_blueprint(register_bp, url_prefix='/register')
app.register_blueprint(todos_bp, url_prefix='/todos')
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(logout_bp, url_prefix='/logout')


if __name__ == "__main__":
    app.run(port=3000)
