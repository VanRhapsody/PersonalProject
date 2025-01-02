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
    return render_template("pages/index.html", active=1)

@app.route("/uloha/<task_id>")
def task(task_id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE id=?",(task_id))
    task=cur.fetchone()
    con.commit()

    cur.execute("SELECT distinct(category) FROM task")
    categories=cur.fetchall()
    con.commit()
    con.close()

    return render_template("pages/uloha.html", task=task, categories=categories)

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
    return render_template("pages/ulohy.html", active=2, tasks=tasks, categories=categories)

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
        return render_template("funcionality_forms/taskadd.html")



@app.route("/kvizy", methods=["POST","GET"])
def kvizy():
    if request.method=="POST":
        global quiz_list
        global quiz_list_index
        global correct_wrong
        global quiz_id_max
        global category_id
        global answers_list
        if session.get("username")==None:
            return render_template("messages/error.html", message="Nelze spustit kvíz, pokud nejste přihlášeni!")
        quiz_list_index=0
        correct_wrong=[]
        count=request.form["count"]
        category=request.form["category"]
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute(f"SELECT id FROM category WHERE name=?", (category,))
        category_id_0=cur.fetchone()
        category_id=category_id_0[0]
        cur.execute(f"SELECT id FROM question ORDER BY id DESC")
        id_max_0=cur.fetchone()
        id_max=id_max_0[0]
        print(category_id)
        #cur.execute(f"SELECT id FROM quiz WHERE category=? AND used=1 ORDER BY id DESC",(category,))
        #quiz_id_max=cur.fetchone()
        #cur.execute(f"SELECT id FROM quiz WHERE category=? AND used=1 ORDER BY id DESC",(category,))
        #quiz_id_allowed_0=cur.fetchall()
        #quiz_id_allowed=[]
        #print(quiz_id_allowed_0)
        #for array in quiz_id_allowed_0:
        #    for element in array:
        #        quiz_id_allowed.append(element)
        con.commit()
        quiz_list=[]
        answers_list=[]
        question=None
        quiz_id_random=0
        for i in range(0, int(count)):
            while (question is None) or (question in quiz_list):
                quiz_id_random=(random.randint(1,int(id_max)))
                cur.execute("SELECT id, prompt, image_url FROM question WHERE category_id=? AND id=?", (category_id,quiz_id_random,))
                question=cur.fetchone()
            quiz_list.append(question)
            correct_wrong.append(None)
        print(quiz_list)
        for id in quiz_list:
            cur.execute("SELECT * FROM answer WHERE quiz_id=? AND is_used==1", (id[0],))
            one_answer=cur.fetchall()
            random.shuffle(one_answer)
            while len(one_answer)<4:
                one_answer.append(['','','',''])
            answers_list.append(one_answer)
        for answer in answers_list:
            print(f"Odpověď: {answer}")
        quiz_list_index=0
        """for id in quiz_id_list:
            cur.execute("SELECT * FROM quiz WHERE id=?",(id,))
            one_task=cur.fetchone()
            question_mix=[one_task[3], one_task[4], one_task[5], one_task[6]]
            question_mix=list(filter(None,question_mix))
            random.shuffle(question_mix)
            one_task=[one_task[0],one_task[1],one_task[2], one_task[8]]
            for question in question_mix:
                one_task.append(question)
                print(f"otázka: {question}")
            for i in range(0,4-len(question_mix)):
                one_task.append("")
            con.commit()
            quiz_list.append(one_task)
            print(f"jedna zamixovaná úloha: {one_task}")"""
        return render_template("pages/quiz.html", active=3, quiz_list=quiz_list, answers_list=answers_list, correct_wrong=correct_wrong, quiz_list_index=quiz_list_index)
    else:
        return render_template("pages/kvizy.html", active=3)
    
@app.route("/kvizy/next", methods=["POST","GET"])
def next_quiz():
    if request.method=="POST":
        global quiz_list
        global correct_wrong
        global quiz_id_max
        global answers_list
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        answer=request.form["answer"]
        print(answer)
        correct_answer=None
        for one_answer in answers_list[quiz_list_index]:
            if one_answer[3]==1:
                correct_answer=one_answer
        if correct_answer[2]==answer:
            correct_wrong[quiz_list_index]=1
        else:
            correct_wrong[quiz_list_index]=0
        print(correct_answer)
        print(correct_wrong)
        """for i, correct_answer in enumerate(correct_answers):
            print(correct_answer)
            if answer==correct_answer[0]:
                correct_wrong[quiz_list_index]=1
                return render_template("pages/quiz.html", answered=True, answer=answer, active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong)
            elif i == len(correct_answers) - 1:
                correct_wrong[quiz_list_index]=0
                return render_template("pages/quiz.html", answered=True, answer=answer, active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong)"""
        return render_template("pages/quiz.html", answered=True, active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong, answer=answer, correct_answer=correct_answer, answers_list=answers_list)
    

@app.route("/kvizy/verify")
def send_answer():
        global quiz_list
        global quiz_list_index
        global correct_wrong
        global quiz_id_max
        global category_id
        print(quiz_list_index)
        for one_answer in answers_list[quiz_list_index]:
            if one_answer[3]==1:
                correct_answer=one_answer
        quiz_list_index+=1
        if int(quiz_list_index)>=int(len(quiz_list)):
            correct=0
            wrong=0
            for element in correct_wrong:
                if element==1:
                    correct+=1
                else:
                    wrong+=1
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("UPDATE user SET quiz_correct = quiz_correct + ?", (correct,))
            cur.execute("UPDATE user SET quiz_absolved = quiz_absolved + 1")
            print(session["id"], category_id)
            cur.execute("UPDATE language_popularity SET value = value + 1 WHERE user_id=? AND category_id=?", (session["id"], category_id))
            con.commit()
            con.close()
            return render_template("pages/kvizy.html", correct=correct, wrong=wrong)
        return render_template("pages/quiz.html", active=3, quiz_list=quiz_list, quiz_list_index=quiz_list_index, correct_wrong=correct_wrong, answers_list=answers_list)


@app.route("/kvizy/add", methods=["POST","GET"])
def add_quiz():
    if request.method=="POST":
        category=request.form["category"]
        description=request.form["description"]
        description=description.split(";")
        correct=request.form["correct"]
        correct=correct.split(";")
        second=request.form["second"]
        second=second.split(";")
        third=request.form["third"]
        third=third.split(";")
        fourth=request.form["fourth"]
        fourth=fourth.split(";")
        list_of_inputs=[description,correct,second,third,fourth]
        max=0
        for input in list_of_inputs:
            if len(input) > max:
                max=len(input)
        for input in list_of_inputs:
            if len(input) < max:
                for i in range(0, (max - len(input))):
                    input.append("")
        for input in list_of_inputs:
            print(input)                           
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        for i in range(0,len(category)):
            cur.execute("INSERT INTO quiz (category, description, correct, second, third, fourth) VALUES (?,?,?,?,?,?)",(category, description[i], correct[i], second[i], third[i], fourth[i]))
            con.commit()
        return redirect(url_for('kvizy'))
    else:
        return render_template("funcionality_forms/quizadd.html")


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
            cur.execute("SELECT id FROM category ORDER BY id DESC")
            category_id_max=cur.fetchone()[0]
            for i in range(1,category_id_max+1):
                cur.execute("INSERT INTO language_popularity(user_id, category_id, value) VALUES (?, ?,?)",(session["id"],i,0,))
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
        cur.execute("SELECT * FROM language_popularity WHERE user_id=?",(session["id"],))
        language_popularity_temporary=cur.fetchall()
        cur.execute("SELECT name FROM category")
        categories=cur.fetchall()
        language_popularity={}
        for i in range (0, len(categories)):
            language_popularity[categories[i]]=language_popularity_temporary[i][3]
        print(language_popularity)
        language_popularity=sorted(language_popularity.items(), key=lambda x: x[1], reverse=True)
        return render_template("pages/profil.html", active=4, username=session["username"], email=session["email"], bio=session["bio"], quiz_correct=quiz_correct, quiz_absolved=quiz_absolved, language_popularity=language_popularity)
    else:
        
        return render_template("profile_forms/register.html", active=4)
    
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
            session["id"]=user[0][0]
            session["username"]=user[0][1]
            session["email"]=user[0][3]
            session["bio"]=user[0][4]
            return render_template("pages/index.html")
        else:
            pass #zobrazení chybové hlášky
        con.commit()
        con.close()
    else:
        return render_template("profile_forms/login.html")
    
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
        return render_template("profile_forms/bio.html")
    
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
        return render_template("profile_forms/email.html")
    
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
        return render_template("profile_forms/password.html")
    
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
        return render_template("profile_forms/username.html")

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