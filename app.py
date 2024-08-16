from flask import Flask, render_template, request, session, flash, url_for, redirect
import sqlite3

app=Flask(__name__)
app.secret_key="Velice tajny klic xddd"


@app.route("/")
def index():
    return render_template("index.html", active=1)

@app.route("/ulohy")
def ulohy():
    return render_template("ulohy.html", active=2)

@app.route("/kvizy")
def kvizy():
    return render_template("kvizy.html", active=3)

@app.route("/profile", methods=["POST","GET"])
def profile():
    if request.method=="POST":
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        username=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        email_duplicate=cur.execute("SELECT email FROM user WHERE email=?",(email,))
        email_duplicate=email_duplicate.fetchall()
        username_duplicate=cur.execute("SELECT username FROM user WHERE username=?",(username,))
        username_duplicate=username_duplicate.fetchall()
        con.commit()
        if username_duplicate and email_duplicate:
            flash("Zadaný E-Mail a uživatelské jméno jsou obsazené!")
            con.close()
            return redirect(url_for("profile"))
        elif email_duplicate:
            flash("Zadaný E-Mail je již obsazený!")
            con.close()
            return redirect(url_for("profile"))
        elif username_duplicate:
            flash("Zadané uživatelské jméno je obsazené!")
            con.close()           
            return redirect(url_for("profile"))
        else:
            cur.execute("INSERT INTO user (username, email, password) VALUES (?,?,?)",(username,email,password))
            con.commit()
            session["username"]=username
            session["email"]=email
            con.close()
            return redirect(url_for("index"))
    elif session.get("username"):
        return render_template("profil.html", active=4, username=session["username"], email=session["email"])
    else:
        print(session.get("username"))
        return render_template("register.html", active=4)


    

"""@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        username=request.form["name"]
        password=request.form["password"]
        session["name"]=username
        cur.execute("INSERT INTO user (username,password) VALUES (?,?)",(username,password))
        con.commit()
        con.close()
    else:
        return render_template("registerinitial.html")"""

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        identifier=request.form["identifier"]
        password=request.form["password"]
        if identifier.__contains__("@"):
            cur.execute("SELECT * FROM user WHERE email=? AND password=?",(identifier,password))
            user=cur.fetchall()
        else:
            cur.execute("SELECT * FROM user WHERE username=? AND password=?",(identifier,password))
            user=cur.fetchall()
        if user:
            session["name"]=user[0][1]
            session["email"]=user[0][3]
            return render_template("index.html")
        else:
            pass
        con.commit()
        con.close()
    else:
        return render_template("login.html")

if __name__=="__main__":
    app.run(debug=True)