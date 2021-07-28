from app import mysql
from werkzeug.security import check_password_hash, generate_password_hash


# POSTS
# Create new post
def insert_post(id_user, title, short_description, content):
    query = "INSERT INTO post (id_user, title, short_description, content) VALUES (%s, %s, %s, %s)"
    values = (id_user, title, short_description, content)
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    cursor.close()


# Get all the posts that are in the database ordered by publication or update date
def get_all_posts():
    query = "SELECT p.id_post, p.id_user, p.title, p.short_description, p.content, p.on_update_dt, u.username " \
            "FROM post p JOIN user u on u.id_user = p.id_user ORDER BY on_update_dt DESC"
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query)
    posts = cursor.fetchall()
    cursor.close()
    return posts


# Get a specific post
def get_post(id_post):
    query = "SELECT p.id_post, p.id_user, p.title, p.short_description, p.content, p.on_update_dt, u.username " \
            "FROM post p JOIN user u on u.id_user = p.id_user WHERE id_post=%s"
    values = (id_post,)
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query, values)
    post = cursor.fetchone()
    cursor.close()
    return post


# Get posts created by a specific user
def get_user_posts(username):
    query = "SELECT p.id_post, p.id_user, p.title, p.short_description, p.content, p.on_update_dt, u.username " \
            "FROM post p JOIN user u on u.id_user = p.id_user WHERE username=%s ORDER BY on_update_dt DESC"
    value = (username,)
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query, value)
    posts = cursor.fetchall()
    cursor.close()
    return posts


# Edit a post
def edit_post(id_post, title, short_description, content):
    query = "UPDATE post SET title=%s, short_description=%s, content=%s WHERE id_post=%s"
    values = (title, short_description, content, id_post)
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    cursor.close()


# USERS
# Create a new user
def insert_user(username, password):
    query = "INSERT INTO user (username, password) VALUES (%s, %s)"
    values = (username, generate_password_hash(password))
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    cursor.close()


# Check of the user already exists
def check_user_exists(username):
    username_exists = False
    query = "SELECT id_user FROM user WHERE username = %s"
    value = (username,)
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query, value)
    # If it is not None, the user exists
    if cursor.fetchone() is not None:
        username_exists = True
        print("Ese usuario ya existe!")
    else:
        print("Ese usuario no existe!")
    cursor.close()
    return username_exists


# Check user data to log in
def check_user_login(username, password):
    query = "SELECT * FROM user WHERE username = %s"
    value = (username,)
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query, value)
    user = cursor.fetchone()
    cursor.close()
    # If password is not correct return None
    if not check_password_hash(user["password"], password):
        print("La contraseña no coincide")
        return None
    # If it is correct return user
    else:
        return user


# Get data from user in session
def get_user_logged_in(id_user):
    query = "SELECT * FROM user WHERE id_user = %s"
    value = (id_user,)
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute(query, value)
    user = cursor.fetchone()
    cursor.close()
    return user
