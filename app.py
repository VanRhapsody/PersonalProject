from flask import Flask, render_template, request, session
import sqlite3

app=Flask(__name__)
con = sqlite3.connect("database.db")
cur = con.cursor()

@app.route("/")
def index():
    return render_template("index.html", active=1)

@app.route("/ulohy")
def ulohy():
    return render_template("ulohy.html", active=2)

@app.route("/profil")
def profil():
    return render_template("profil.html", active=4)

@app.route("/kvizy")
def kvizy():
    return render_template("kvizy.html", active=3)

@app.route("/register", methods=["GET","POST"])
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
        return render_template("registerinitial.html")

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        username=request.form["name"]
        password=request.form["password"]
        cur.execute("SELECT * FROM user WHERE username=? AND password=?",(username,password))
        user=cur.fetchall()
        if user:
            session["name"]=username
            return render_template("index.html")
        
        else:
            pass
        con.commit()
        con.close()
    else:
        return render_template("logininitial.html")

if __name__=="__main__":
    app.run(debug=True)