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
    print(session.get("username"))
    if request.method=="POST":
        con = sqlite3.connect("user.db")
        cur = con.cursor()
        username=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        bio=request.form["bio"]
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
            cur.execute("INSERT INTO user (username, email, password,bio) VALUES (?,?,?,?)",(username,email,password,bio))
            con.commit()
            session["bio"]=bio
            session["username"]=username
            session["email"]=email
            
            con.close()
            return redirect(url_for("index"))
    elif "username" in session:
        return render_template("profil.html", active=4, username=session["username"], email=session["email"], bio=session["bio"])
    else:
        
        return render_template("register.html", active=4)
    
@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        con = sqlite3.connect("user.db")
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
            session["username"]=user[0][1]
            session["email"]=user[0][3]
            session["bio"]=user[0][4]
            return render_template("index.html")
        else:
            pass #zobrazení chybové hlášky
        con.commit()
        con.close()
    else:
        return render_template("login.html")
    
@app.route("/change_bio", methods=["POST","GET"])
def change_bio():
    if request.method=="POST":
        bio=request.form["bio"]
        session["bio"]=bio
        con = sqlite3.connect("user.db")
        cur = con.cursor()
        cur.execute("UPDATE user SET bio=? WHERE username=?",(bio,session["username"]))
        con.commit()
        con.close()
        return redirect(url_for("profile"))
    else:
        return render_template("bio.html")
    
@app.route("/change-email", methods=["POST","GET"])
def change_email():
    if request.method=="POST":
        email=request.form["email"]
        session["email"]=email
        con = sqlite3.connect("user.db")
        cur = con.cursor()
        cur.execute("UPDATE user SET email=? WHERE username=?",(email,session["username"]))
        con.commit()
        con.close()
        return redirect(url_for("profile"))
    else:
        return render_template("email.html")
    
@app.route("/change-password", methods=["POST","GET"])
def change_password():
    if request.method=="POST":
        password=request.form["password"]
        session["password"]=password
        con = sqlite3.connect("user.db")
        cur = con.cursor()
        cur.execute("UPDATE user SET password=? WHERE username=?",(password,session["username"]))
        con.commit()
        con.close()
        return redirect(url_for("profile"))
    else:
        return render_template("password.html")
    
@app.route("/change-username", methods=["POST","GET"])
def change_username():
    if request.method=="POST":
        username=request.form["username"]
        con = sqlite3.connect("user.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE username=?",(username,))
        con.commit()
        user=cur.fetchall()
        if user:
            pass
        else:      
            cur.execute("UPDATE user SET username=? WHERE username=?",(username,session["username"]))
            session["username"]=username
            con.commit()
            con.close()
            return redirect(url_for("profile"))
    else:
        return render_template("username.html")

    


    

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



if __name__=="__main__":
    app.run(debug=True)