from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from todoitis.auth import login_required
from todoitis.db import get_db

bp = Blueprint('tasks', __name__)

@login_required
@bp.route('/')
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT p.id, task_name, task_desc,due_date,due_time, author_id, username'
        ' FROM tasks p JOIN user u ON p.author_id = u.id'
        ' ORDER BY due_date,due_time'
    ).fetchall()
    return render_template('tasks/index.html', tasks=tasks)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['taskname']
        desc = request.form['description']
        duetime=request.form['duetime']
        duedate=request.form['duedate']
        print(duetime,"///",duedate)
        error = None

        if not name:
            error = 'Task name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tasks (task_name, task_desc,due_time,due_date,author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, desc,duetime,duedate,g.user['id'])
            )
            db.commit()
            return redirect(url_for('tasks.index'))

    return render_template('tasks/create.html')

def get_task(id, check_author=True):
    task = get_db().execute(
        'SELECT t.id, task_name, task_desc, due_date, due_time, author_id, username'
        ' FROM tasks t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_author and task['author_id'] != g.user['id']:
        abort(403)

    return task

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        taskname = request.form['taskname']
        taskdesc = request.form['description']
        error = None

        if not taskname:
            error = 'Task name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tasks SET task_name = ?, task_desc = ?'
                ' WHERE id = ?',
                (taskname, taskdesc, id)
            )
            db.commit()
            return redirect(url_for('tasks.index'))

    return render_template('tasks/update.html', task=task)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('tasks.index'))