from flask import Flask, render_template, request, session, flash, url_for, redirect
import sqlite3
from collections import OrderedDict
import random

app=Flask(__name__)
app.secret_key="Velice tajny klic xddd"

quiz_list=[]
quiz_list_index=0
correct_wrong=[]
quiz_id_max=0
category=""

@app.route("/")
def index():
    return render_template("index.html", active=1)

@app.route("/uloha/<task_id>")
def task(task_id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE task_id=?",(task_id))
    task=cur.fetchone()
    con.commit()

    cur.execute("SELECT distinct(category) FROM task")
    categories=cur.fetchall()
    con.commit()
    con.close()

    return render_template("uloha.html", task=task, categories=categories)

@app.route("/ulohy/", defaults={'categories':None})
@app.route("/ulohy/<categories>") #do routování se zadá jazyk - např. sql a  to se ptoom předá jako vstupní parametr funkce, která z databáze získá všechny instance, kde jazyk je sql a zobrazí je
def tasks(categories):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    if categories is None:
        cur.execute("SELECT * FROM task")
    else:
        cur.execute("SELECT * FROM task WHERE category=?",(categories,))
    con.commit()
    tasks=cur.fetchall()
    cur.execute("SELECT DISTINCT(category) FROM task")
    con.commit()
    categories=cur.fetchall()
    print(categories)
    print(tasks)
    return render_template("ulohy.html", active=2, tasks=tasks, categories=categories)

@app.route("/ulohy/add", methods=["POST","GET"])
def add_task():
    if request.method=="POST":
        title=request.form["title"]
        category=request.form["category"]
        difficulty=request.form["difficulty"]
        description=request.form["description"]
        solution=request.form["solution"]
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("INSERT INTO task (title, category, difficulty, description, solution) VALUES (?,?,?,?,?)",(title,category,difficulty,description,solution,))
        con.commit()
        return redirect(url_for("tasks"))
    else:
        return render_template("taskadd.html")



@app.route("/kvizy", methods=["POST","GET"])
def kvizy():
    if request.method=="POST":
        global quiz_list
        global quiz_list_index
        global correct_wrong
        global quiz_id_max
        global category
        if session.get("username")==None:
            return render_template("error.html", message="Nelze spustit kvíz, pokud nejste přihlášeni!")
        quiz_list=[]
        quiz_list_index=0
        correct_wrong=[]
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("SELECT id FROM quiz ORDER BY id DESC")
        quiz_id_max=cur.fetchone()
        con.commit()
        count=request.form["count"]
        category=request.form["language"]
        quiz_id_list=[]
        for i in range(0, int(count)):
            quiz_id_random=(random.randint(1,int(quiz_id_max[0])))
            while quiz_id_random in quiz_id_list:
                quiz_id_random=(random.randint(1,int(quiz_id_max[0])))
            quiz_id_list.append(quiz_id_random)
            correct_wrong.append(None)
        for id in quiz_id_list:
            cur.execute("SELECT * FROM quiz WHERE id=?",(id,))
            one_task=cur.fetchone()
            question_mix=[one_task[3], one_task[4], one_task[5], one_task[6]]
            question_mix=list(filter(None,question_mix))
            random.shuffle(question_mix)
            one_task=[one_task[0],one_task[1],one_task[2]]
            for question in question_mix:
                one_task.append(question)
            for i in range(0,4-len(question_mix)):
                one_task.append("")
            con.commit()
            quiz_list.append(one_task)
        print(category)
        return render_template("quiz.html", active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong)
    else:
        return render_template("kvizy.html", active=3)
    
@app.route("/kvizy/next", methods=["POST","GET"])
def next_quiz():
    if request.method=="POST":
        global quiz_list
        global quiz_list_index
        global correct_wrong
        global quiz_id_max
        print(correct_wrong)
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("SELECT correct FROM quiz")
        correct_answers=cur.fetchall()
        answer=request.form["answer"]
        for i, correct_answer in enumerate(correct_answers):
            print(correct_answer)
            if answer==correct_answer[0]:
                correct_wrong[quiz_list_index]=1
                return render_template("quiz.html", answered=True, answer=answer, active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong)
            elif i == len(correct_answers) - 1:
                correct_wrong[quiz_list_index]=0
                return render_template("quiz.html", answered=True, answer=answer, active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong)
        return render_template("quiz.html", active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong)
    

@app.route("/kvizy/verify")
def send_answer():
        global quiz_list
        global quiz_list_index
        global correct_wrong
        global quiz_id_max
        global category
        quiz_list_index+=1
        if int(quiz_list_index)>=int(quiz_id_max[0]):
            correct=0
            wrong=0
            for element in correct_wrong:
                if element==1:
                    correct+=1
                else:
                    wrong+=1
            print(correct)
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("UPDATE user SET quiz_correct = quiz_correct + ?", (correct,))
            cur.execute("UPDATE user SET quiz_absolved = quiz_absolved + 1")
            cur.execute(f"UPDATE languagepopularity SET {category} = {category} + 1")
            con.commit()
            con.close()
            return render_template("kvizy.html", correct=correct, wrong=wrong)
        return render_template("quiz.html", active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong)


@app.route("/kvizy/add", methods=["POST","GET"])
def add_quiz():
    if request.method=="POST":
        category=request.form["category"]
        description=request.form["description"]
        correct=request.form["correct"]
        second=request.form["second"]
        third=request.form["third"]
        fourth=request.form["fourth"]
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("INSERT INTO quiz (category, description, correct, second, third, fourth) VALUES (?,?,?,?,?,?)",(category, description, correct, second, third, fourth))
        con.commit()
        return redirect(url_for('kvizy'))
    else:
        return render_template("quizadd.html")


@app.route("/profile", methods=["POST","GET"])
def profile():
    print(session.get("username"))
    if request.method=="POST":
        con = sqlite3.connect("database.db")
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
            cur.execute("SELECT id FROM user where username=?",(username,))
            id=cur.fetchone()
            print(id[0])
            session["id"]=id[0]
            cur.execute("INSERT INTO languagepopularity(id) VALUES (?)",(session["id"],))
            session["bio"]=bio
            session["username"]=username
            session["email"]=email
            print(session["id"])
            con.commit()
            con.close()
            return redirect(url_for("index"))
    elif "username" in session:
        
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("SELECT quiz_correct, quiz_absolved FROM user WHERE username=?",(session["username"],))
        quiz_correct, quiz_absolved=cur.fetchone()
        cur.execute("SELECT * FROM languagepopularity WHERE id=?",(session["id"],))
        language_popularity=cur.fetchall()
        print(language_popularity)
        language_popularity_temporary={}
        language_names=["Algoritmizace","C","C#","Java","Python","SQL"]
        for i in range (0, len(language_names)):
            language_popularity_temporary[language_names[i]]=language_popularity[0][i+1]
            print(language_names[i], language_popularity[0][i])
        language_popularity_temporary=sorted(language_popularity_temporary.items(), key=lambda x: x[1], reverse=True)
        print(language_popularity_temporary)
        return render_template("profil.html", active=4, username=session["username"], email=session["email"], bio=session["bio"], quiz_correct=quiz_correct, quiz_absolved=quiz_absolved, language_popularity_temporary=language_popularity_temporary)
    else:
        
        return render_template("register.html", active=4)
    
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
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("UPDATE user SET bio=? WHERE username=?",(bio,session["username"]))
        con.commit()
        con.close()
        return redirect(url_for("profile"))
    else:
        return render_template("bio.html")
    
@app.route("/change_email", methods=["POST","GET"])
def change_email():
    if request.method=="POST":
        email=request.form["email"]
        session["email"]=email
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("UPDATE user SET email=? WHERE username=?",(email,session["username"]))
        con.commit()
        con.close()
        return redirect(url_for("profile"))
    else:
        return render_template("email.html")
    
@app.route("/change_password", methods=["POST","GET"])
def change_password():
    if request.method=="POST":
        password=request.form["password"]
        session["password"]=password
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("UPDATE user SET password=? WHERE username=?",(password,session["username"]))
        con.commit()
        con.close()
        return redirect(url_for("profile"))
    else:
        return render_template("password.html")
    
@app.route("/change_username", methods=["POST","GET"])
def change_username():
    if request.method=="POST":
        username=request.form["username"]
        con = sqlite3.connect("database.db")
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

@app.route("/logout")
def logout():
    session.pop("username",None)
    session.pop("password",None)
    session.pop("email",None)
    session.pop("bio",None)
    return redirect(url_for('index'))


    


    

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

    """
    {% if answer == quiz_list[quiz_list_index][3] and quiz_list[quiz_list_index][3]!=None %}
        <span class="quiz-content-answer" style="background-color:var(--active-green) !important">
        {% else %}
        <span class="quiz-content-answer">
        {% endif %}
            {% if quiz_list[quiz_list_index][3]==None %}
            <input type="radio" name="answer" value="{{ quiz_list[quiz_list_index][3] }}" disabled>
            {% else %}
            <input type="radio" name="answer" value="{{ quiz_list[quiz_list_index][3] }}">
            {% endif %}
            <label for="first_answer">{{ quiz_list[quiz_list_index][3] }}</label>
        </span>
        <br>
        {% if answer == quiz_list[quiz_list_index][4] and quiz_list[quiz_list_index][4]!=None %}
        <span class="quiz-content-answer" style="background-color:var(--active-green) !important">
        {% else %}
        <span class="quiz-content-answer">
        {% endif %}
            {% if quiz_list[quiz_list_index][4]==None %}
            <input type="radio" name="answer" value="{{ quiz_list[quiz_list_index][4] }}" disabled>
            {% else %}
            <input type="radio" name="answer" value="{{ quiz_list[quiz_list_index][4] }}">
            {% endif %}
            <label for="second_answer">{{ quiz_list[quiz_list_index][4] }}</label>
        </span>
        <br>
        {% if answer == quiz_list[quiz_list_index][5] and quiz_list[quiz_list_index][5]!=None %}
        <span class="quiz-content-answer" style="background-color:var(--active-green) !important">
        {% else %}
        <span class="quiz-content-answer">
        {% endif %}
            {% if quiz_list[quiz_list_index][5]==None %}
            <input type="radio" name="answer" value="{{ quiz_list[quiz_list_index][5] }}" disabled>
            {% else %}
            <input type="radio" name="answer" value="{{ quiz_list[quiz_list_index][5] }}">
            {% endif %}
            <label for="third_answer">{{ quiz_list[quiz_list_index][5] }}</label>
        </span>
        <br>
        {% if answer == quiz_list[quiz_list_index][6] and quiz_list[quiz_list_index][6]!=None %}
        <span class="quiz-content-answer" style="background-color:var(--active-green) !important">
        {% else %}
        <span class="quiz-content-answer">
        {% endif %}
        {% if quiz_list[quiz_list_index][6]==None %}
        <input type="radio" name="answer" value="{{ quiz_list[quiz_list_index][6] }}" disabled>
        {% else %}
        <input type="radio" name="answer" value="{{ quiz_list[quiz_list_index][6] }}">
        {% endif %}
            <label for="fourth_answer">{{ quiz_list[quiz_list_index][6] }}</label>
        </span>
        <br>
    """