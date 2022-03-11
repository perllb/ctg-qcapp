from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
app = Flask(__name__)

basedir = "/srv/flask/qcapp/"
app.config['BASEDIR'] = basedir
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +  basedir + "db_ctg.sqlite/db.sqlite"
app.config['STATIC_FOLDER'] = basedir + "/qcapp/static"
app.config['QC_FOLDER'] = basedir + "/qcapp/static/ctg-qc"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['USE_PERMANENT_SESSION'] = False

db.init_app(app)

#create all db tables
@app.before_first_request
def create_tables():
    from .models import CTGdata
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from .models import User, CTGdata

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

# blueprint for auth routes in our app
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

# blueprint for listers of app
from .listers import listers as listers_blueprint
app.register_blueprint(listers_blueprint)

# blueprint for ctgdata of app
from .ctgdata import ctgdata_blue as ctgdata_blueprint
app.register_blueprint(ctgdata_blueprint)

# blueprint for guides of app
from .guides import guides as guides_blueprint
app.register_blueprint(guides_blueprint)
