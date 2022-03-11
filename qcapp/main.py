from flask import Blueprint, render_template
from . import db
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy

# import upstream file
import importlib.util
spec = importlib.util.spec_from_file_location("module.name", "/path/to/file.py")
foo = importlib.util.module_from_spec(spec)


main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html')

@main.route('/news')
@login_required
def news():
    new_proj,new_interop,days = listnewfiles()
    return render_template('news.html',new_proj=new_proj,new_interop=new_interop,days=days)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html',name=current_user.name,email=current_user.email)

#@login_required
#def project_info():
#    return render_template('project_info.html',name=current_user.name,email=current_user.email)
