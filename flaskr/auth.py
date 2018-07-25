import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    # Need to take this out after everything is working
    # session.clear()
    ##
    user_id = session.get('user_id')
    print('CURRENT USER ID: ', user_id)

    if user_id is None:
        g.user = None
    else:
        cursor = get_db().cursor()
        # print(cursor)
        cursor.execute("SELECT * FROM person WHERE id = %s", (user_id,))
        g.user = cursor.fetchone()
        # g.user = get_db().execute(
        # g.user = cursor.execute(
        #     # 'SELECT * FROM user WHERE id = ?', (user_id,)
        #     "SELECT * FROM person WHERE id = %s", (user_id,)
        # ).fetchone()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        # elif db.execute (
        else:
            cursor.execute (
                # 'SELECT id FROM user WHERE username = ?', (username,)
                "SELECT id FROM person WHERE username = %s", (username,)
            )
            if cursor.fetchone() is not None:
                error = 'User {} is already registered'.format(username)

        if error is None:
            # db.execute(
            cursor.execute (
                # 'INSERT INTO user (username, password) VALUES (?, ?)',
                "INSERT INTO person (username, password) VALUES (%s, %s)",
                (username, generate_password_hash(password),)
                # (username, password,)
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
        cursor.execute (
            # 'SELECT * FROM user WHERE username = ?', (username,)
            "SELECT * FROM person WHERE username = %s", (username,)
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
    # return redirect(url_for('index'))
    # return redirect(url_for('auth.login'))
    return redirect(url_for('verify'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
            # return redirect(url_for('home'))

        return view(**kwargs)

    return wrapped_view
