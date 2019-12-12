from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import os

bp = Blueprint('blog', __name__)


@bp.route('/home')
def home():
    db = get_db()
    cursor = db.cursor()
    # user_id = session.get('user_id')
    #
    # if user_id is None:
    #     return render_template()
    # posts = db.execute (
    #     'SELECT p.id, title, body, rating, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()
    cursor.execute(
        "SELECT l.id, title, body, rating, created, author_id, username"
        " FROM log l JOIN user p ON l.author_id=p.id"
        " ORDER BY created DESC"
    )
    posts = cursor.fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        rating = request.form['rating']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO log (title, body, rating, author_id)'
                ' VALUES (%s, %s, %s, %s)', (title, body, rating, g.user[0])
            )
            db.commit()

            return redirect(url_for('mine.mine'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    cursor = get_db().cursor()
    cursor.execute(
        'SELECT l.id, title, body, rating, created, author_id, username'
        ' FROM log l JOIN user p ON l.author_id = p.id'
        ' WHERE l.id = %s', (id,)
    )
    post = cursor.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist".format(id))

    print('POSTha: {}, USER: {}'.format(post[3], g.user[0]))
    if check_author and post[5] != g.user[0]:
        print('NOPE!')
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        print('TITLE: ', title)
        body = request.form['body']
        print('BODY: ', body)
        rating = request.form['rating']
        print('RATING: ', rating)
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'UPDATE log SET title = %s, body = %s, rating = %s'
                ' WHERE id = %s',
                (title, body, rating, id)
            )
            # db.execute(
            #     'UPDATE post SET title = ?, body = ?, rating = ?'
            #     ' WHERE id = ?',
            #     (title, body, rating, id)
            # )
            db.commit()
            # return redirect(url_for('blog.index'))
            return redirect(url_for('mine.mine'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM log WHERE id = %s', (id,))
    # db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    # return redirect(url_for('blog.index'))
    return redirect(url_for('mine.mine'))
