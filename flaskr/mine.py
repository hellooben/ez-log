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
    cursor = db.cursor()
    user_id = session.get('user_id')
    cursor.execute(
        'SELECT l.id, title, body, rating, created, author_id, username'
        ' FROM log l INNER JOIN person ON person.id=l.author_id'
        # ' WHERE author_id = ?', (user_id,)
        ' WHERE author_id = {uID}'
        ' ORDER BY created DESC'.\
        format(uID=user_id)
    )
    # g.user = get_db().execute(
    #     'SELECT * FROM user WHERE id = ?', (user_id,)
    # ).fetchone()
    #
    # if user_id is None:
    #     return render_template()
    # posts = db.execute (
    #     # 'SELECT p.id, title, body, created, author_id, username'
    #     # ' FROM post p JOIN user u WHERE p.author_id == u.id'
    #     # # ' FROM post p'
    #     # # ' WHERE u.id=p.author_id'
    #     # ' ORDER BY created DESC'
    #     'SELECT post.id, title, body, rating, created, author_id, username'
    #     ' FROM post INNER JOIN user ON user.id=post.author_id'
    #     # ' WHERE author_id = ?', (user_id,)
    #     ' WHERE author_id = {uID}'
    #     ' ORDER BY created DESC'.\
    #     format(uID=user_id)
    # ).fetchall()
    posts = cursor.fetchall()
    return render_template('blog/mine.html', posts=posts)

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
            # return redirect(url_for('blog.index'))
            return redirect(url_for('mine.mine'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    cursor = get_db().cursor()
    cursor.execute(
        'SELECT l.id, title, body, rating, created, author_id, username'
        ' FROM log l JOIN person p ON l.author_id = p.id'
        ' WHERE l.id = %s', (id,)
    )
    post = cursor.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist".format(id))

    print('POSTMINE: {}, USERMINE: {}'.format(post[5], g.user[0]))
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
