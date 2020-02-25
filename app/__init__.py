from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect
from flask_moment import Moment
from flask_avatars import Avatars
import os


basedir = os.path.abspath(os.path.dirname(__file__))

csrf = CsrfProtect()
app = Flask(__name__)
login = LoginManager(app)
bootstrap = Bootstrap(app)
csrf.init_app(app)
moment = Moment(app)
avatars = Avatars(app)

app.config['SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "app.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models