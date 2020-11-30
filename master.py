from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "repetition_legitimizes"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    password = db.Column("password", db.String(100))
    points = db.Column("points", db.Integer)

    def __init__(self, name, password, points):
        self.name = name
        self.password = password
        self.points = points

@app.route("/", methods=["POST", "GET"])
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form['submit_button'] == 'Sign In':
            user = request.form["nm"]
            session["user"] = user
            pw = request.form["ps"]
            session["password"] = pw
            found_user = users.query.filter_by(name=user).first()
            if found_user:
                if found_user.password == pw:
                    session["points"] = found_user.points
                else:
                    flash("Incorrect password, try again.")
                    return render_template("login.html")
            else:
                session["points"] = 0;
                usr = users(user, pw, 0)
                db.session.add(usr)
                db.session.commit()
            flash("User Login Successful")
            return redirect(url_for("home"))
        elif request.form['submit_button'] == "Continue as Guest":
            session["user"] = "Guest"
            session["password"] = "samplePass"
            session["points"] = 69
            flash("Login Successful (Guest)")
            return redirect(url_for("home"))
    else:
        if "user" in session:
            flash("Login Successful (Previous Login)")
            return redirect(url_for("home"))
        return render_template("login.html")

@app.route("/home")
def home():
    if "user" in session:
        user = session["user"]
        pw = session["password"]
        pts = session["points"]
        sorted_users = sorted(users.query.all(), key=lambda x: x.points, reverse=True)
        name = []
        points = []
        for i in range(0,3):
            #if hasattr(sorted_users[i], "name"):
            try:
                name.append(sorted_users[i].name)
                points.append(sorted_users[i].points)
            #else:
            except IndexError:
                name.append("N/A")
                points.append(0)

        return render_template("home.html", name=user, password=pw, points=pts, firstuser=name[0], firstpoints=points[0], seconduser=name[1], secondpoints=points[1], thirduser=name[2], thirdpoints=points[2])
    flash("User not in session")
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
    flash("Logout Successful", "info")
    session.pop("user", None)
    session.pop("password", None)
    return redirect(url_for("login"))

@app.route("/deleet")
def deleet():
    if "user" in session:
        user = session["user"]
        if user == "Guest":
            users.query.filter_by(name=user).delete()
            db.session.commit()
            flash("Account deleted (Temporary Guest account)")
        else:
            users.query.filter_by(name=user).delete()
            db.session.commit()
            flash("Account deleted")
    else:
        flash("Signed out of Guest account")
    session.pop("user", None)
    session.pop("password", None)
    return redirect(url_for("login"))

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
