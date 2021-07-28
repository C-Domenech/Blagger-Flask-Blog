from flask import Flask, render_template, request, redirect, url_for, flash, session, g, Markup
from flask_mysqldb import MySQL
from flask_paginate import Pagination, get_page_args
import json
import re

# APP CREATION
app = Flask(__name__)

# GET DATABASE CONFIGURATION
with open("config.json") as json_data:
    config = json.load(json_data)

app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['MYSQL_HOST'] = config['MYSQL_HOST']
app.config['MYSQL_PORT'] = config['MYSQL_PORT']
app.config['MYSQL_USER'] = config['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = config['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = config['MYSQL_DB']
app.config['MYSQL_CURSORCLASS'] = config['MYSQL_CURSORCLASS']
app.config['MYSQL_DATABASE_CHARSET'] = config['MYSQL_DATABASE_CHARSET']

# DEV CONFIGURATION
# app.config['SECRET_KEY'] = 'dev'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_PORT'] = 3306
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'root'
# app.config['MYSQL_DB'] = 'blog_db'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# app.config['MYSQL_DATABASE_CHARSET'] = 'utf-8'

# INITIALIZE DATABASE
mysql = MySQL(app)

import database as db


# Index -> Home route -> Show all posts
@app.route('/')
def index():
    posts = db.get_all_posts()
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    pagination_posts, total = get_posts_by_page(posts, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4', alignment='center')
    return render_template('posts.html', posts=pagination_posts, page=page, per_page=per_page, pagination=pagination)


# Route to posts from an user -> Show all posts created by that user
@app.route('/<string:username>')
def posts_by_user(username):
    user_posts = db.get_user_posts(username)
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    pagination_posts, total = get_posts_by_page(user_posts, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4', alignment='center')
    return render_template('posts.html', posts=pagination_posts, page=page, per_page=per_page, pagination=pagination)


# Get posts per page
def get_posts_by_page(posts, offset=0, per_page=10):
    return posts[offset: offset + per_page], len(posts)


# Post route
@app.route('/<int:id_post>')
def selected_post(id_post):
    post = db.get_post(id_post)
    return render_template('post.html', post=post, content=Markup(post['content']))


# Route to form -> Create posts
@app.route('/new_post', methods=('GET', 'POST'))
def new_post():
    # Check there is an user log in
    if g.user is not None:
        # Check request.method and the form activated
        if request.method == 'POST' and 'new_post_form' in request.form:
            title = request.form['title']
            short_description = request.form['short_description']
            content = request.form['content-editor']
            db.insert_post(g.user['id_user'], title, short_description, content)
            flash('Post creado correctamente', 'alert-success')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    return render_template('new_post_form.html')


# Route to a filled form -> Edit posts
@app.route('/edit_post/<int:id_post>', methods=('GET', 'POST'))
def edit_post(id_post):
    # Get the specific post
    post = db.get_post(id_post)
    # Check there is an user log in and it is the post owner
    if g.user is not None and g.user['id_user'] == post['id_user']:
        # Check request.method and the form activated
        if request.method == 'POST' and 'edit_post_form' in request.form:
            title = request.form['title']
            short_description = request.form['short_description']
            content = request.form['content-editor']
            db.edit_post(id_post, title, short_description, content)
            flash('Post editado correctamente', 'alert-success')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    return render_template('edit_post_form.html', post=post)


# Route to a sign up form
@app.route('/sign_up', methods=('GET', 'POST'))
def sign_up():
    if session.get('id_user') is None:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            # Check if the username already exists
            if not db.check_user_exists(username):
                db.insert_user(username, password)
                flash('Bienvenido a la comunidad de Blagger!', 'alert-success')
                session.clear()
                session['id_user'] = db.check_user_login(username, password)['id_user']
                return redirect(url_for('index'))
            else:
                flash('Ese usuario ya existe', 'alert-warning')
        return render_template('new_user_form.html')
    else:
        return redirect(url_for('index'))


# Route to login form
@app.route('/login', methods=('GET', 'POST'))
def login():
    if session.get('id_user') is None:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            # Check if the username exists
            if db.check_user_exists(username):
                user = db.check_user_login(username, password)
                if user is not None:
                    # Clear the current session
                    session.clear()
                    # Add the id of the logged in user to the session
                    session['id_user'] = user['id_user']
                    print("Sesión iniciada")
                    return redirect(url_for('index'))
                else:
                    flash('La contraseña es incorrecta', 'alert-danger')
            else:
                flash('El usuario es incorrecto', 'alert-danger')
        return render_template('login_form.html')
    else:
        return redirect(url_for('index'))


# Method that runs before every view function (before index and others views functions), it checks if the user id is
# stored in the session
@app.before_request
def load_user_already_logged_in():
    id_user = session.get('id_user')
    if id_user is None:
        g.user = None
    else:
        g.user = db.get_user_logged_in(id_user)


# Logout user -> Clear the session -> Redirect to home
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
