from flask import Flask, render_template, request, session, flash, url_for, redirect
import sqlite3
from collections import OrderedDict
import bcrypt
import random

app=Flask(__name__)
app.secret_key="Velice tajny klic xddd"

salt=bcrypt.gensalt()

def db_connect():
    con = sqlite3.connect("database.db") #připojení do databáze uložené v adresáři jako database.db
    cur = con.cursor() #vytvoření cursor pro interakci s databází
    return cur, con

@app.route("/")
def index():
    return render_template("pages/index.html", active=1) # active reprezentuje, jaká stránka je momentálně aktivní a má se tak zvýraznit v navbaru

@app.route("/users")
def users():
    cur, con=db_connect()
    cur.execute("SELECT id, username,email FROM user")
    users=cur.fetchall()
    return render_template("pages/users.html", users=users)

@app.route("/users/<user_id>")
def user(user_id):
    cur, con=db_connect()
    cur.execute("SELECT username, email, bio, quiz_correct, quiz_absolved FROM user WHERE id=?", (user_id,))
    username, email, bio, quiz_correct, quiz_absolved=cur.fetchone()
    cur.execute("SELECT quiz_correct, quiz_absolved FROM user WHERE username=?",(session["username"],))
    quiz_correct, quiz_absolved=cur.fetchone()
    cur.execute("SELECT * FROM language_popularity WHERE user_id=?",(session["id"],))
    language_popularity_temporary=cur.fetchall()
    cur.execute("SELECT name FROM category")
    categories=cur.fetchall()
    language_popularity={}
    for i in range (0, len(categories)):
        language_popularity[categories[i]]=language_popularity_temporary[i][3]
    language_popularity=sorted(language_popularity.items(), key=lambda x: x[1], reverse=True)
    return render_template("pages/profil.html", active=4, username=username, email=email, bio=bio, quiz_correct=quiz_correct, quiz_absolved=quiz_absolved, language_popularity=language_popularity)

@app.route("/kvizy", methods=["POST","GET"])
def kvizy():
    if request.method=="POST":
        if session.get("username")==None: #Pokud uživatel není přihlášen, tedy proměnná session["username"] je prázdná, tak se vypíše chybová hláška
            return render_template("messages/error.html", message="Nelze spustit kvíz, pokud nejste přihlášeni!")
        session["quiz_list_index"]=0 #quiz list index slouží k procházení jednotlivých kvízů, které byly pro uživatele vygenerovány
        session["correct_wrong"]=[] #correct_wrong je list na začátku obsahující samé nuly a na základě správné či špatné odpovědi u konkrétní otázky v kvízu se nastaví na 1 nebo 0
        count=request.form["count"] #count reprezentuje počet zvolených otázek (5, 10)
        category=request.form["category"] #category reprezentuje vybranou kategorii (Python, C#)
        cur, con=db_connect() #využití funkce db connect pro připojení k db
        cur.execute(f"SELECT id FROM category WHERE name=?", (category,)) #vybrání všech id z tabulky kategorie, kde se jméno kategorie rovná zvolenému jménu (python, cs)
        category_id=cur.fetchone() #spojení jednoho výsledku do proměnné category_id
        session["category_id"]=category_id[0] #přiřazení nultého indexu (všechny tyto proměnné se ukládají jako tuple) do proměnné session["category_id"]
        cur.execute(f"SELECT id FROM question ORDER BY id DESC") #vybrání všech id z tabulky question při jejich sestupném řazení
        id_max=cur.fetchone() #přiřazení jednoho výsledku dotazu (nejvyššího možného id) do proměnné id_max
        id_max=id_max[0] #přiřazení nultého indexu id_max (uchovává se jako tuple) do stejné proměnné
        session["quiz_list"]=[] #vytvoření session["quiz_list"] pro uchování jednotlivých otázek v kvízech
        session["answers_list"]=[] #vytvoření session["answers_list"] pro uchování jednotlivých odpovědí ke kvízům a zda jsou správné
        for i in range(0, int(count)): #založení for cyklu pro generaci náhodných otázek n-krát podle počtu zvolených kvízů
            question=None #nastavení question na None pro možnost jeho kontroly, zda je none
            while (question is None) or (question in session["quiz_list"]): #kontrola, jestli je Question none nebo jestli už je v proměnné quiz_list pro zamezení existenci duplikátních otázek
                quiz_id_random=(random.randint(1,int(id_max))) #generování náhodného kvízu pro volbu jedné otázky v rozmezí od 1 do maxima
                cur.execute("SELECT id, prompt, image_url FROM question WHERE category_id=? AND id=?", (session["category_id"],quiz_id_random,)) #vybrání id, slovního zadání a případného obrázku pro jednu konkrétní vybranou otázku se stejným id jako vygenerovaným a stejným category_id jako zvolená kategorie
                question=cur.fetchone() #přiřazení jedné otázky do proměnné question

            session["quiz_list"].append(question) #přidání question jako list do quiz_list
            session["correct_wrong"].append(None) #přidání nulové hodnoty do correct_wrong při úspěšném vytvoření jedné otázky
        for id in session["quiz_list"]: #založení for each cyklu vybírajícího id jednotlivých otázek 
            cur.execute("SELECT * FROM answer WHERE quiz_id=? AND is_used==1", (id[0],)) #vybrání jedné odpovědi, kde quiz_id je roven zvolené kategorii a otázka je použita na základě is_used
            one_answer=cur.fetchall() #přiřazení jedné hodnoty z dotazu do proměnné one_answer
            random.shuffle(one_answer) #náhodné 
            while len(one_answer)<4:
                one_answer.append(['','','','']) #přidávání prázdných listů do one_answer, dokud její délka nebudou 4 listy, protože na každé stránce kvízu se zobrazují čtyři políčka pro odpověď 
            session["answers_list"].append(one_answer) #přidání jedné odpovědi do dvojrozměrného listu answers_list
        return render_template("pages/quiz.html", active=3) 
    else:
        return render_template("pages/kvizy.html", active=3)
    
@app.route("/kvizy/next", methods=["POST","GET"])
def next_quiz():
    if request.method=="POST":
        cur, con=db_connect() #využití funkce db connect pro připojení k db
        answer=request.form["answer"] #získání hodnoty answer z formu na kviz.html

        correct_answer=None #nastavení correct answer na None pro možnost následného přiřazení správné odpovědi
        for one_answer in session["answers_list"][session["quiz_list_index"]]: #založení for cyklu pro procházení answers list, a to v nestnuntém listu pro quiz_list_index reprezentující konkrétní otázku
            if one_answer[3]==1: #kontrola, jestli se hodnota reprezentující is_correct u dané otázky rovná 1
                correct_answer=one_answer #přiřazení zvolené one_answer do correct

        if correct_answer[2]==answer: #v případě, že odpověď uživatele je rovna slovnímu zadání správné odpovědi
            session["correct_wrong"][session["quiz_list_index"]]=1 #tak correct_wrong se na daném indexu změní na 1
        else:
            session["correct_wrong"][session["quiz_list_index"]]=0 #v opačném případě (špatná odpověď) se změní na 0
        session.modified=True #bez použití této funkce se z nějakého důvodu correct_wrong vždy vymazalo na samé None
        return render_template("pages/quiz.html", answered=True, active=3, answer=answer, correct_answer=correct_answer)
    

@app.route("/kvizy/verify")
def send_answer():
        session["quiz_list_index"]+=1 #zvýšení quiz_list_index o 1 značící přesun na další kvíz
        if int(session["quiz_list_index"])>=int(len(session["quiz_list"])): #pokud je zvýšený quiz_list_index větší než quiz_list, tedy už počet otázek, dojde k ukončení kvízu
            correct=0
            wrong=0
            #nastavení correct a wrong na 0 pro možnost jejich inkrementace
            for element in session["correct_wrong"]: #založení for each cyklu pro průchod correct wrong
                if element==1: #pokud se daný element rovná 1, inkrementuje se correct
                    correct+=1
                else:
                    wrong+=1
            cur, con=db_connect()
            cur.execute("UPDATE user SET quiz_correct = quiz_correct + ?", (correct,)) #zvýšení počtu správných odpovědí u uživatele o hodnotu correct
            cur.execute("UPDATE user SET quiz_absolved = quiz_absolved + 1") #inkrementace počtu absolvovaných kvízů
            cur.execute("UPDATE language_popularity SET value = value + 1 WHERE user_id=? AND category_id=?", (session["id"], session["category_id"],)) #zvýšení popularity konkrétní kategorie u uživatele na základě category_id
            con.commit()
            con.close()
            return render_template("pages/kvizy.html", correct=correct, wrong=wrong)
        return render_template("pages/quiz.html", active=3)


@app.route("/kvizy/add", methods=["POST","GET"])
def add_quiz():
    if request.method=="POST":
        category=request.form["category"] #získání parametru kategorie z formu
        description=request.form["description"] #získání parametru slovního zadání kvízu z formu
        description=description.split(";") #rozdělení parametru na list na základě středníků pro možnost vložení více záznamů najednou
        correct=request.form["correct"] #získání parametru pro správnou odpověď
        correct=correct.split(";")
        second=request.form["second"] #získání parametru pro první špatnou odpověď
        second=second.split(";")
        third=request.form["third"] #získání parametru pro druhou špatnou odpověď
        third=third.split(";")
        fourth=request.form["fourth"] #získání parametru pro třetí špatnou odpověď
        fourth=fourth.split(";")
        list_of_inputs=[description,correct,second,third,fourth] #vytvoření listu jednotlivých vícehodntových atributů
        print(list_of_inputs)
        max=0
        for input in list_of_inputs:
            if len(input) > max:
                max=len(input)
        for input in list_of_inputs: #vyplnění dílčích inputů prázdným textem na základě toho, jestli je jeho délka menší než zjištěná maximální délka největšího inputu (např. vyplnění prázdných odpovědí u třetí a čtvrté odpovědi při volbě pouze A,B)
            if len(input) < max:
                for i in range(0, (max - len(input))):
                    input.append("")
                        
        cur, con=db_connect()
        cur.execute("SELECT quiz_id FROM answer ORDER BY quiz_id DESC")
        quiz_id=cur.fetchall()
        quiz_id=quiz_id[0][0]
        for i in range(0,max):
            cur.execute("INSERT INTO question(prompt, category_id) VALUES (?,?)",(list_of_inputs[0][i], category))
            is_correct=1
            cur.execute("INSERT INTO answer(quiz_id, text, is_correct) VALUES (?,?,?)",(quiz_id, list_of_inputs[1][i], is_correct))
            is_correct=0
            cur.execute("INSERT INTO answer(quiz_id, text, is_correct) VALUES (?,?,?)",(quiz_id, list_of_inputs[2][i], is_correct))
            cur.execute("INSERT INTO answer(quiz_id, text, is_correct) VALUES (?,?,?)",(quiz_id, list_of_inputs[3][i], is_correct))
            cur.execute("INSERT INTO answer(quiz_id, text, is_correct) VALUES (?,?,?)",(quiz_id, list_of_inputs[4][i], is_correct))
            con.commit()
        return redirect(url_for('kvizy'))
    else:
        return render_template("funcionality_forms/quizadd.html")


@app.route("/profile", methods=["POST","GET"])
def profile():
    if request.method=="POST":
        cur, con = db_connect()
        username=request.form["name"]
        email=request.form["email"]
        password = b'' + request.form["password"].encode('utf-8')
        
        hashed_password=bcrypt.hashpw(password, salt)
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
            cur.execute("INSERT INTO user (username, email, password,bio) VALUES (?,?,?,?)",(username,email,hashed_password,bio))
            cur.execute("SELECT id FROM user where username=?",(username,))
            id=cur.fetchone()

            session["id"]=id[0]
            cur.execute("SELECT id FROM category ORDER BY id DESC")
            category_id_max=cur.fetchone()[0]
            for i in range(1,category_id_max+1):
                cur.execute("INSERT INTO language_popularity(user_id, category_id, value) VALUES (?, ?,?)",(session["id"],i,0,))
            session["bio"]=bio
            session["username"]=username
            session["email"]=email

            con.commit()
            con.close()
            return redirect(url_for("index"))
    elif "username" in session:
        cur, con = db_connect()
        cur.execute("SELECT quiz_correct, quiz_absolved FROM user WHERE username=?",(session["username"],))
        quiz_correct, quiz_absolved=cur.fetchone()
        cur.execute("SELECT * FROM language_popularity WHERE user_id=?",(session["id"],))
        language_popularity_temporary=cur.fetchall()
        cur.execute("SELECT name FROM category")
        categories=cur.fetchall()
        language_popularity={}
        for i in range (0, len(categories)):
            language_popularity[categories[i]]=language_popularity_temporary[i][3]
        language_popularity=sorted(language_popularity.items(), key=lambda x: x[1], reverse=True)
        return render_template("pages/profil.html", active=4, username=session["username"], email=session["email"], bio=session["bio"], quiz_correct=quiz_correct, quiz_absolved=quiz_absolved, language_popularity=language_popularity)
    else:
        
        return render_template("profile_forms/register.html", active=4)
    
@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        con = sqlite3.connect("database.db")
        cur, con = db_connect()
        identifier=request.form["identifier"]
        password = b'' + request.form["password"].encode('utf-8')
        hashed_password=bcrypt.hashpw(password, salt)
        print()
        if identifier.__contains__("@"):
            cur.execute("SELECT * FROM user WHERE email=? AND password=?",(identifier,hashed_password))
            user=cur.fetchall()
        else:
            cur.execute("SELECT * FROM user WHERE username=? AND password=?",(identifier,hashed_password))
            user=cur.fetchall()
        if user:
            session["id"]=user[0][0]
            session["username"]=user[0][1]
            session["email"]=user[0][3]
            session["bio"]=user[0][4]
            return render_template("pages/index.html")
        else:
            return render_template("error.html", message="Uživatel nenalezen!")
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
        cur, con = db_connect()
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
        cur, con = db_connect()
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
        cur, con = db_connect()
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
        cur, con = db_connect()
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


if __name__=="__main__":
    app.run()
