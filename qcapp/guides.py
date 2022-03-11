import os
import re
from flask import Blueprint,render_template, jsonify
from flask_login import login_required, current_user
import datetime as dt
import glob
import csv
import pandas as pd

guides = Blueprint('guides', __name__)

# List projects html files (for new runs)
@guides.route('/sheet_info')
@login_required
def sheetguide():
    return render_template('samplesheet_guide.html')
