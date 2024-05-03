from flask import Flask, render_template

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/kvizy")
def kvizy():
    return render_template("kvizy.html")

@app.route("/profil")
def profil():
    return render_template("profil.html")

@app.route("/ulohy")
def ulohy():
    return render_template("ulohy.html")

if __name__=="__main__":
    app.run()