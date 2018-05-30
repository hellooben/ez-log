from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('mine', __name__)

@bp.route('/my_logs')
def mine():
    db = get_db()
    user_id = session.get('user_id')
    # g.user = get_db().execute(
    #     'SELECT * FROM user WHERE id = ?', (user_id,)
    # ).fetchone()
    #
    # if user_id is None:
    #     return render_template()
    posts = db.execute (
        # 'SELECT p.id, title, body, created, author_id, username'
        # ' FROM post p JOIN user u WHERE p.author_id == u.id'
        # # ' FROM post p'
        # # ' WHERE u.id=p.author_id'
        # ' ORDER BY created DESC'
        'SELECT post.id, title, body, created, author_id, username'
        ' FROM post INNER JOIN user ON user.id=post.author_id'
        # ' WHERE author_id = ?', (user_id,)
        ' WHERE author_id = {uID}'
        ' ORDER BY created DESC'.\
        format(uID=user_id)
    ).fetchall()
    return render_template('blog/mine.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)', (title, body, g.user['id'])
            )
            db.commit()
            # return redirect(url_for('blog.index'))
            return redirect(url_for('home'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?', (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            # return redirect(url_for('blog.index'))
            return redirect(url_for('home'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    # return redirect(url_for('blog.index'))
    return redirect(url_for('home'))
