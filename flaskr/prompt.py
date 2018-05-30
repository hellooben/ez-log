from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('prompt', __name__)

@bp.route('/', methods=('GET', 'POST'))
def verify():
    return render_template('blog/home.html')
