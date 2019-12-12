import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from pdb import set_trace

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    print('CURRENT USER ID: ', user_id)

    if user_id is None:
        g.user = None
    else:
        cursor = get_db().cursor()

        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        g.user = cursor.fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        set_trace()
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        else:
            # Looking for another user with the same username
            # Here, SQL can be injected
            query = "SELECT id FROM user WHERE username = '%s'" % username

            # The query to be executed
            print('QUERY: ', query)

            # Executing the query. Injected SQL can be ran here
            cursor.execute(
                query
            )
            if cursor.fetchone() is not None:
                error = 'User {} is already registered'.format(username)

        if error is None:
            cursor.execute(
                "INSERT INTO user (username, password) VALUES (%s, %s)",
                (username, generate_password_hash(password),)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None
        cursor.execute(
            "SELECT * FROM user WHERE username = %s", (username,)
        )
        user = cursor.fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('home'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('verify'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
