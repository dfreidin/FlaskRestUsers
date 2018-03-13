from flask import Flask, render_template, request, redirect, flash
from mysqlconnection import MySQLConnector
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "swordfish"
mysql = MySQLConnector(app, 'users')
@app.route('/users')
def index():
    query = "SELECT id, CONCAT(first_name, ' ', last_name) AS name, email, DATE_FORMAT(created_at, '%M %D, %Y') AS created FROM users;"
    users = mysql.query_db(query)
    return render_template('index.html', all_users=users)
@app.route("/users/new")
def new():
    return render_template("new.html")
@app.route("/users/create", methods=["POST"])
def create():
    fn = request.form["first_name"]
    ln = request.form["last_name"]
    em = request.form["email"]
    if len(fn) < 1 or len(ln) < 1 or len(em) < 1:
        flash("All fields must be entered")
        return redirect("/users/new")
    if not EMAIL_REGEX.match(em):
        flash("Invalid email address")
        return redirect("/users/new")
    query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUES(:first_name, :last_name, :email, NOW(), NOW());"
    query_data = {"first_name": fn, "last_name": ln, "email": em}
    id = mysql.query_db(query, query_data)
    return redirect("/users/"+str(id))
@app.route("/users/<id>")
def show(id):
    query = "SELECT id, CONCAT(first_name, ' ', last_name) AS name, email, DATE_FORMAT(created_at, '%M %D, %Y') AS created FROM users WHERE id = :id;"
    query_data = {"id": id}
    users = mysql.query_db(query, query_data)
    if len(users) < 1:
        return redirect("/users")
    return render_template("show.html", user=users[0])
@app.route("/users/<id>/edit")
def edit(id):
    query = "SELECT id, first_name, last_name, email FROM users WHERE id = :id;"
    query_data = {"id": id}
    users = mysql.query_db(query, query_data)
    if len(users) < 1:
        return redirect("/users")
    return render_template("edit.html", user=users[0])
@app.route("/users/<id>", methods=["POST"])
def update(id):
    fn = request.form["first_name"]
    ln = request.form["last_name"]
    em = request.form["email"]
    if len(fn) < 1 or len(ln) < 1 or len(em) < 1:
        flash("All fields must be entered")
        return redirect("/users/"+str(id)+"/edit")
    if not EMAIL_REGEX.match(em):
        flash("Invalid email address")
        return redirect("/users/"+str(id)+"/edit")
    query = "UPDATE users SET first_name = :first_name, last_name = :last_name, email = :email, updated_at = NOW() WHERE id = :id;"
    query_data = {"first_name": fn, "last_name": ln, "email": em, "id": id}
    mysql.query_db(query, query_data)
    return redirect("/users/"+str(id))
@app.route("/users/<id>/destroy")
def destroy(id):
    query = "DELETE FROM users WHERE id = :id;"
    query_data = {"id": id}
    mysql.query_db(query, query_data)
    return redirect("/users")
app.run(debug=True)