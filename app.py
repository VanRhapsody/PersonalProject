from flask import Flask, render_template, request, session, flash, url_for, redirect
import sqlite3
import bcrypt
import random

app=Flask(__name__) # založení proměnné app s názvem __name__
app.secret_key="Velice tajny klic xddd" # založení tajného klíče pro možnost založení session

def db_connect():
    con = sqlite3.connect("database.db") # připojení do databáze uložené v adresáři jako database.db
    cur = con.cursor() # vytvoření cursor pro interakci s databází
    return cur, con

@app.route("/") # route pro zobrazení domovské stránky
def index():
    return render_template("pages/index.html", active=1) #  active reprezentuje, jaká stránka je momentálně aktivní a má se tak zvýraznit v navbaru

@app.route("/users") # route pro zobrazení všech už. profilů
def users():
    cur, con=db_connect()
    cur.execute("SELECT id, username,email FROM user") # vybrání id, už. jména a e-mailu z tabulky user
    users=cur.fetchall() # spojení výsledku dotazu do proměnné users
    return render_template("pages/users.html", users=users) # přesměrování na stránku users.html s předaným parametrem users

@app.route("/users/<user_id>") # route pro zobrazení konkrétního už. profilu
def user(user_id):
    cur, con=db_connect()
    cur.execute("SELECT username, email, bio, quiz_correct, quiz_absolved FROM user WHERE id=?", (user_id,)) # vybrání už. jména, e-mailu, bia, počtu správných odpovědí a absolvovaných kvízů z tabulky user v záznamech, kde se id rovná předanému parametru
    username, email, bio, quiz_correct, quiz_absolved=cur.fetchone() # spojení výsledku dotazu do stejnojmenných proměnných 
    cur.execute("SELECT * FROM language_popularity WHERE user_id=?",(user_id,)) # vybrání všech atributů z tabulky language_popularity
    language_popularity_temporary=cur.fetchall() # spojení výsledku do dotazu language popularity
    cur.execute("SELECT name FROM category") # výběr jmen kategorií z tabulky category
    categories=cur.fetchall() # spojení výsledku dotazu do tabulky categories
    language_popularity={} # založení dictionary language_popularity
    for i in range (0, len(categories)): # založení for cyklu pro procházení jednotlivých dílčích kategorií 
        language_popularity[categories[i]]=language_popularity_temporary[i][3] # nastavení hodnoty v language_popularity s klíčem categories[i], tedy dílčí kategorie, na hodnotu třetí hodnotu v i-tém listu v language_popularity_temporary
    language_popularity=sorted(language_popularity.items(), key=lambda x: x[1], reverse=True) # language_popularity.items přetvoří dictionary na list, ve kterém jsou další listy, které vždy obsahující dvojici klíč a k ní hodnota
    # tento list se následně seřadí s klíčem pro řazení jako druhou (první) hodnotou v listech, což je právě hodnota popularity jazyku
    # nakonec je reverse nastaveno na True pro sestpné řazení
    return render_template("pages/profil.html", active=2, username=username, email=email, bio=bio, quiz_correct=quiz_correct, quiz_absolved=quiz_absolved, language_popularity=language_popularity, is_admin=0)

@app.route("/kvizy", methods=["POST","GET"])
def kvizy():
    if request.method=="POST":
        if session.get("username")==None: # Pokud uživatel není přihlášen, tedy proměnná session["username"] je prázdná, tak se vypíše chybová hláška
            return render_template("messages/error.html", message="Nelze spustit kvíz, pokud nejste přihlášeni!")
        session["quiz_list_index"]=0 # quiz list index slouží k procházení jednotlivých kvízů, které byly pro uživatele vygenerovány
        session["correct_wrong"]=[] # correct_wrong je list na začátku obsahující samé nuly a na základě správné či špatné odpovědi u konkrétní otázky v kvízu se nastaví na 1 nebo 0
        count=request.form["count"] # count reprezentuje počet zvolených otázek (5, 10)
        category=request.form["category"] # category reprezentuje vybranou kategorii (Python, C# )
        cur, con=db_connect() # využití funkce db connect pro připojení k db
        cur.execute(f"SELECT id FROM category WHERE name=?", (category,)) # vybrání všech id z tabulky kategorie, kde se jméno kategorie rovná zvolenému jménu (python, cs)
        category_id=cur.fetchone() # spojení jednoho výsledku do proměnné category_id
        session["category_id"]=category_id[0] # přiřazení nultého indexu (všechny tyto proměnné se ukládají jako tuple) do proměnné session["category_id"]
        cur.execute(f"SELECT id FROM question ORDER BY id DESC") # vybrání všech id z tabulky question při jejich sestupném řazení
        id_max=cur.fetchone() # přiřazení jednoho výsledku dotazu (nejvyššího možného id) do proměnné id_max
        id_max=id_max[0] # přiřazení nultého indexu id_max (uchovává se jako tuple) do stejné proměnné
        session["quiz_list"]=[] # vytvoření session["quiz_list"] pro uchování jednotlivých otázek v kvízech
        session["answers_list"]=[] # vytvoření session["answers_list"] pro uchování jednotlivých odpovědí ke kvízům a zda jsou správné
        for i in range(0, int(count)): # založení for cyklu pro generaci náhodných otázek n-krát podle počtu zvolených kvízů
            question=None # nastavení question na None pro možnost jeho kontroly, zda je none
            while (question is None) or (question in session["quiz_list"]): # kontrola, jestli je Question none nebo jestli už je v proměnné quiz_list pro zamezení existenci duplikátních otázek
                quiz_id_random=(random.randint(1,int(id_max))) # generování náhodného kvízu pro volbu jedné otázky v rozmezí od 1 do maxima
                cur.execute("SELECT id, prompt, image_url FROM question WHERE category_id=? AND id=?", (session["category_id"],quiz_id_random,)) # vybrání id, slovního zadání a případného obrázku pro jednu konkrétní vybranou otázku se stejným id jako vygenerovaným a stejným category_id jako zvolená kategorie
                question=cur.fetchone() # přiřazení jedné otázky do proměnné question
            session["quiz_list"].append(question) # přidání question jako list do quiz_list
            session["correct_wrong"].append(None) # přidání nulové hodnoty do correct_wrong při úspěšném vytvoření jedné otázky
        for id in session["quiz_list"]: # založení for each cyklu vybírajícího id jednotlivých otázek 
            cur.execute("SELECT * FROM answer WHERE quiz_id=? AND is_used==1", (id[0],)) # vybrání jedné odpovědi, kde quiz_id je roven zvolené kategorii a otázka je použita na základě is_used
            one_answer=cur.fetchall() # přiřazení jedné hodnoty z dotazu do proměnné one_answer
            random.shuffle(one_answer) # náhodné zamixování otázek 
            session["answers_list"].append(one_answer) # přidání jedné odpovědi do dvojrozměrného listu answers_list
        con.close() # uzavření connection z bezpečnostních důvodů 
        return render_template("pages/quiz.html", active=3) 
    else:
        return render_template("pages/kvizy.html", active=3)
    
@app.route("/kvizy/next", methods=["POST","GET"])
def next_quiz():
    if request.method=="POST":
        answer=request.form["answer"] # získání hodnoty answer z formu na kviz.html
        correct_answer=None # nastavení correct answer na None pro možnost následného přiřazení správné odpovědi
        for one_answer in session["answers_list"][session["quiz_list_index"]]: # založení for cyklu pro procházení answers list, a to v nestnuntém listu pro quiz_list_index reprezentující konkrétní otázku
            if one_answer[3]==1: # kontrola, jestli se hodnota reprezentující is_correct u dané otázky rovná 1
                correct_answer=one_answer # přiřazení zvolené one_answer do correct

        if correct_answer[2]==answer: # v případě, že odpověď uživatele je rovna slovnímu zadání správné odpovědi
            session["correct_wrong"][session["quiz_list_index"]]=1 # tak correct_wrong se na daném indexu změní na 1
        else:
            session["correct_wrong"][session["quiz_list_index"]]=0 # v opačném případě (špatná odpověď) se změní na 0
        session.modified=True # bez použití této funkce se z nějakého důvodu correct_wrong vždy vymazalo na samé None
        return render_template("pages/quiz.html", answered=True, active=3, answer=answer, correct_answer=correct_answer)
    

@app.route("/kvizy/verify")
def send_answer():
        session["quiz_list_index"]+=1 # zvýšení quiz_list_index o 1 značící přesun na další kvíz
        if int(session["quiz_list_index"])>=int(len(session["quiz_list"])): # pokud je zvýšený quiz_list_index větší než quiz_list, tedy už počet otázek, dojde k ukončení kvízu
            correct=0
            wrong=0
            # nastavení correct a wrong na 0 pro možnost jejich inkrementace
            for element in session["correct_wrong"]: # založení for each cyklu pro průchod correct wrong
                if element==1: # pokud se daný element rovná 1, inkrementuje se correct
                    correct+=1
                else:
                    wrong+=1
            cur, con=db_connect()
            cur.execute("UPDATE user SET quiz_correct = quiz_correct + ?", (correct,)) # zvýšení počtu správných odpovědí u uživatele o hodnotu correct
            cur.execute("UPDATE user SET quiz_absolved = quiz_absolved + 1") # inkrementace počtu absolvovaných kvízů
            cur.execute("UPDATE language_popularity SET value = value + 1 WHERE user_id=? AND category_id=?", (session["id"], session["category_id"],)) # zvýšení popularity konkrétní kategorie u uživatele na základě category_id
            con.commit() # commitnutí výsledku dotazu do databáze 
            con.close() # uzavření connection z bezpečnostních důvodů
            return render_template("pages/kvizy.html", correct=correct, wrong=wrong)
        return render_template("pages/quiz.html", active=3)


@app.route("/kvizy/add", methods=["POST","GET"])
def add_quiz():
    if request.method=="POST":
        cur, con=db_connect()
        category=request.form["category"] # získání parametru kategorie z formu
        description=request.form["description"] # získání parametru slovního zadání kvízu z formu
        description=description.split(";") # rozdělení parametru na list na základě středníků pro možnost vložení více záznamů najednou
        correct=request.form["correct"] # získání parametru pro správnou odpověď
        correct=correct.split(";")
        second=request.form["second"] # získání parametru pro první špatnou odpověď
        second=second.split(";")
        third=request.form["third"] # získání parametru pro druhou špatnou odpověď
        third=third.split(";")
        fourth=request.form["fourth"] # získání parametru pro třetí špatnou odpověď
        fourth=fourth.split(";")
        list_of_inputs=[description,correct,second,third,fourth] # vytvoření listu jednotlivých vícehodntových atributů
        max=0
        for input in list_of_inputs:
            if len(input) > max:
                max=len(input)
        for input in list_of_inputs: # vyplnění dílčích inputů prázdným textem na základě toho, jestli je jeho délka menší než zjištěná maximální délka největšího inputu (např. vyplnění prázdných odpovědí u třetí a čtvrté odpovědi při volbě pouze A,B)
            if len(input) < max:
                for i in range(0, (max - len(input))):
                    input.append("")
        
        cur.execute("SELECT id FROM category WHERE name=?", (category, ))
        category_id=cur.fetchall()[0][0]
        cur.execute("SELECT id FROM question ORDER BY id DESC") # vybrání quiz_id v dotazu a jeho řazení sestupně, pro získání maximálního id
        quiz_id=cur.fetchall()
        quiz_id=quiz_id[0][0]+1 # nastavení quiz id na nultý index nultého listu, z nějakého důvodu jsou výsledky vraceny takhle
        #přičtení 1, protože vložená otázka kvízu logicky nemůže mít stejné ID jako ta poslední dosud vložená
        for i in range(0,max): # vytvoření for cyklu pro počet vložených otázek do kvízů daný počtem max
            cur.execute("INSERT INTO question(prompt, category_id) VALUES (?,?)",(list_of_inputs[0][i], category_id)) # vložení konkrétní otázky v rámci kvízu do tabulky question na základě quiz_id
            is_correct=1 # nastavení is correct na 1, protože jako první se vkládá správná odpověď
            cur.execute("INSERT INTO answer(quiz_id, text, is_correct) VALUES (?,?,?)",(quiz_id, list_of_inputs[1][i], is_correct)) # vložení odpovědi ve formuláři označené jako správné do tabulky answers s hodnotou is correct 1
            is_correct=0 # nastavení is correct na 0, protože všechny další odpovědi jsou špatné
            for j in range(2,5): # založení for cyklu pro vložení tří špatnýc odpovědí do tabulky answer
                cur.execute("INSERT INTO answer(quiz_id, text, is_correct) VALUES (?,?,?)",(quiz_id, list_of_inputs[j][i], is_correct)) # vložení špatné odpovědi s nastaveným is correct na 0
            con.commit() # commitnutí do databáze, to je nutné, když se tam něco vkládá
            quiz_id+=1 # zvýšení quiz_id o jedna v případě vkládání více otázek najednou
        return redirect(url_for('kvizy')) #  přesměrování na stránku pro kvízy
    else:
        return render_template("funcionality_forms/quizadd.html") #  v případě, že metodou není post, zůstaň na stránce s formulářem pro přidání kvízu

#kvizy delete je route, která se aktivuje při volby odstranit kvíz u admina a poskytne stránku, kde si vybere kategorii
#v rámci které chce kvíz odstranit
@app.route("/kvizy/delete")
def category_choose():
    cur,con=db_connect()
    cur.execute("SELECT * FROM category") #vybrání všeho z tabulky category pro možnost zobrazení jednotlivých kategorií v tabulce
    categories=cur.fetchall() #spojení všech výsledků dotazu do proměnné categories
    return render_template("pages/categorychoose.html", categories=categories) #přesměrování na stránku s výběrem kategorií s předáním proměnné categories

@app.route("/kvizy/delete/<category_id>")
def quiz_choose(category_id):
    cur, con=db_connect()
    cur.execute("SELECT name FROM category WHERE id=?", (category_id, )) #vybrání jména z kategorie pro záznamy, kde se id rovná hledanému id kategorie
    category=cur.fetchone() #spojení výsledku dotazu do proměnné category, fetchone, protože logicky se pro dané id vrátí jen jeden záznam
    category=category[0] #nastavení kategorie na nultý list, protože z nějakého důvodu vrací tuple
    cur.execute("SELECT id, prompt, is_used FROM question WHERE category_id=?", (category_id, )) #vybrání id, otázky a is_used z question
    #id, aby bylo možné při kliknutí na otázku ji jednoznačně identifiovat v db
    #otázku pro zobrazení otázky v kvízu
    #a is_used, protože se nesmí zobrazovat už "odstraněné otázky"
    questions=cur.fetchall() #spojení výsledků dotazu do proměnné questions
    return render_template("pages/deletequiz.html", questions=questions, category=category) #předání stránky pro odstranění konkrétního kvízu, předání parametrů questions a category

#důvod, proč funkce pro zobrazení kvízů a odstranění kvízů jsou odlišené je, že ta předchozí funkce pouze vykresluje seznam kvízů k odstranění
#zatímco tato funkce slouží jako funkcionalita pro odstranění kvízu a vykoná se po kliknutí na odkaz "Smazat"
@app.route("/kvizy/delete/action/<quiz_id>")
def quiz_delete(quiz_id):
    cur,con=db_connect()
    cur.execute("UPDATE question SET is_used=0 WHERE id=?", (quiz_id, )) #nastavení is_used u vybrané otázky na 0, aby nemohla být použita
    cur.execute("UPDATE answer SET is_used=0 WHERE quiz_id=?", (quiz_id, )) #nastavení is_used u odpovědí k vybrané otázce na 0, aby nemohly být použity
    con.commit() #commitnutí výsledků do databáze, aby se projevily
    return redirect(url_for("index")) #přesměrování na funkci index pro vykreslení domovské stránky

@app.route("/profile", methods=["POST","GET"])
def profile():
    if request.method=="POST":
        cur, con = db_connect()
        username=request.form["name"] # získání username z formuláře na příslušené stránce
        email=request.form["email"] # získání emailu z formuláře
        password = b'' + request.form["password"].encode('utf-8') # získání hesla ve formátu Python Bytes a jejcih zakódování pomocí utf-8 pro možnost zahashování
        salt=bcrypt.gensalt() # vygenerování náhodné soli pro ozvláštnění hesla
        hashed_password=bcrypt.hashpw(password, salt) # zahashování hesla pomocí soli vytvořené 
        bio=request.form["bio"] # získání bia z formuláře
        email_duplicate=cur.execute("SELECT email FROM user WHERE email=?",(email,)) # výběr emailu z databáze, kde se rovná zadanému e-mailu pro předcházení duplicitním účtům
        email_duplicate=email_duplicate.fetchall() # spojení výsledků dotazu do email_duplicate
        username_duplicate=cur.execute("SELECT username FROM user WHERE username=?",(username,)) # výběr username databáze za stejným účelem jako u emailu
        username_duplicate=username_duplicate.fetchall() # spojení výsledků dotazu do username_duplicate
        if username_duplicate and email_duplicate: # pokud jsou e-mail i uživatelské jméno obsazené, vypíše se chybová hláška
            return render_template("messages/error.html", message="Zadaný E-Mail a uživatelské jméno jsou obsazené!")
        elif email_duplicate: # pokud je e-mail obsazený, vypíše se chybová hláška
            return render_template("messages/error.html", message="Zadaný E-Mail je obsazený!")
        elif username_duplicate: # pokud je už. jméno obsazené, vypíše se chybová hláška          
            return render_template("messsages/error.html", message="Zadané uživatelské jméno je obsazené!")
        else: # pokud není nic obsazené
            cur.execute("INSERT INTO user (username, email, password,bio) VALUES (?,?,?,?)",(username,email,hashed_password,bio)) # vložení username, zahashovaného hesla a bia do tabulky user
            cur.execute("SELECT id FROM user where username=?",(username,)) # získání id z tabulky user na základě vloženého username
            id=cur.fetchone() # spojení id do proměnné id
            session["id"]=id[0] # nastavení session["id"] na nultý index pro id kvůli tomu, že se furt získává jako list
            cur.execute("SELECT id FROM category ORDER BY id DESC") # získání maximálního id z tabulky category
            category_id_max=cur.fetchone()[0] # spojení maximáního id do proměnné category_id
            for i in range(1,category_id_max+1): # založení for cyklu pro vkládání nulových hodnot do tabulky langugage_popularity
                #  v případě, že by se toto neudělalo, vyhazovalo by zobrazení profilu uživatele chybu, protože by nebylo možné získat údaje o popualritě jazyků
                cur.execute("INSERT INTO language_popularity(user_id, category_id, value) VALUES (?, ?,?)",(session["id"],i,0,))
            session["bio"]=bio
            session["username"]=username
            session["email"]=email
            # nastavení promenných v rámci session na získané údaje z původního formuláře
            con.commit() # commitnutí výsledků dotazů, toto se v souvislost s insert musí dělat vždy
            con.close()
            return redirect(url_for("index")) # vrácení na stránku pod funkcí index
    elif "username" in session: # pokud už session obsahuje proměnnou s názvem username, zobrazí se místo toho už. profil
        cur, con = db_connect()
        cur.execute("SELECT is_admin, quiz_correct, quiz_absolved FROM user WHERE username=?",(session["username"],)) # vybrání hodnot pro úpspěšně zodpovězené otázky a počet absolvovaných kvízů z tabulky, kde je username rovno session["username"]
        is_admin, quiz_correct, quiz_absolved=cur.fetchone() # spojení výsledku dotazu do proměnných quiz_correct a quiz_absolved
        cur.execute("SELECT * FROM language_popularity WHERE user_id=?",(session["id"],)) # vybrání všech hodnot z tabulky language popularity, kde id uživatele je rovno session["id"]
        language_popularity_temporary=cur.fetchall() # spojení výsledku dotazu do proměnné language_popularity, která je v tomto kontextu list
        cur.execute("SELECT name FROM category") # vybrání všech hodnot atributu name z tabulky category pro získání všech kategorií (C, Python, ...)
        categories=cur.fetchall() # spojení výsledku dotazu do proměnné categories
        language_popularity={} # vytvoření dictionary language_popularity
        for i in range (0, len(categories)): # vytvoření for cyklu pro procházení jednotlivých získaných kategorií 
            language_popularity[categories[i]]=language_popularity_temporary[i][3] # nastavení záznam v language popularities s klíčem obsahujícím název kategorie na získaný language_popularity pro tuto kategorii (v language_popularity se jedná o i-tý list a jeho třetí hodnotu)
        language_popularity=sorted(language_popularity.items(), key=lambda x: x[1], reverse=True) # language_popularity.items přetvoří dictionary na list, ve kterém jsou další listy, které vždy obsahující dvojici klíč a k ní hodnota
        # tento list se následně seřadí s klíčem pro řazení jako druhou (první) hodnotou v listech, což je právě hodnota popularity jazyku
        # nakonec je reverse nastaveno na True pro sestpné řazení
        return render_template("pages/profil.html", active=4, username=session["username"], email=session["email"], bio=session["bio"], quiz_correct=quiz_correct, quiz_absolved=quiz_absolved, language_popularity=language_popularity, is_admin=is_admin)
    else: # pokud není metoda post a uživatel ani nemá uživatelské jméno v session, předá se formulář pro registraci
        
        return render_template("profile_forms/register.html", active=4)
    
@app.route("/login",methods=["POST","GET"]) # route pro login uživatele
def login():
    if request.method=="POST": # pokud je metoda post
        cur, con = db_connect()
        identifier=request.form["identifier"] # získání identifier z formuláře, může se jednat o uživatelské jméno nebo heslo
        user_password = request.form["password"].encode('utf-8') # převedení hesla do formátu pybtes a jeho zakódování pomocí utf-8 pro možnost zahashování
        cur.execute("SELECT password FROM user WHERE email=? OR username=?",(identifier,identifier)) # vybrání zahashovaného hesla na základě identifikátoru uživatele, kterým může být uživatelské jméno nebo email
        password=cur.fetchone()[0] # spojení výsledku dotazu do proměnné password
        result=bcrypt.checkpw(user_password, password) # porovnání získáného hesla z databáze a z formuláře pomocí funkce checkpw, ta na prvním místě vyžaduje heslo přímo v bytech a na druhém místě heslo zahashované
        if result: # pokud je result hodnota True
            cur.execute("SELECT * FROM user WHERE email=? OR username=?", (identifier, identifier)) # vybrání všech atributů z tabulky user, kde identifikátor (už. jméno nebo e-mail) se rovná hodnotě zadané ve formuláři
            user=cur.fetchall() # spojení výledku dotazu do proměnné user
            print(user)
            session["id"]=user[0][0] # nastavení session["id"] na nultou hodnotu v nultém listu v proměnné user
            session["username"]=user[0][1] # na první hodnotu v nultém listu
            session["email"]=user[0][2] # na druhou hodnotu v nultém listu
            session["bio"]=user[0][4] # na třetí hodnotu v nultém listu
            return render_template("pages/index.html")
        else:
            return render_template("messages/error.html", message="Uživatel nenalezen!") # přesměrování na stránku s chybovou hlášku o tom, že uživatel nebyl nalezen
    else: # pokud metoda není post, přesměruje se uživatel na stránku s formulářem pro login
        return render_template("profile_forms/login.html")
    
@app.route("/change_bio", methods=["POST","GET"]) # route pro změnu bia uživatele
def change_bio():
    if request.method=="POST": # pokud je metoda post
        bio=request.form["bio"] # získání bia z formuláře
        session["bio"]=bio # nastavení získaného bia do proměnné session["bio"]
        cur, con = db_connect()
        cur.execute("UPDATE user SET bio=? WHERE username=?",(bio,session["username"])) # aktualizace atributu bio na hodnotu z formuláře pro záznamy, kde se uživatelské jméno rovná session["username"]
        con.commit() # commitnutí výsledků do tabulky, aby se změna projevila
        return redirect(url_for("profile")) # přesměrování na funkci pro zobrazení uživatelského profilu
    else: # pokud metoda není post, přesměruje se uživatel na stránku s formulářem pro změnu bia
        return render_template("profile_forms/bio.html") 
    
@app.route("/change_email", methods=["POST","GET"]) # route pro změnu e-mailu uživatele
def change_email():
    if request.method=="POST": # pokud je metoda post
        email=request.form["email"] # získání e-mailu z formuláře
        session["email"]=email # nastavení session["email"] na hodnotu získanou z formuláře
        cur, con = db_connect()
        cur.execute("UPDATE user SET email=? WHERE username=?",(email,session["username"])) # aktualizace atributu email na hodnotu z formuláře pro záznamy, kde se e-mail rovná session["email"]
        con.commit() # commitnutí výsledku dotazu do databáze
        return redirect(url_for("profile")) # přesměrování na funkci pro zobrazení uživatelského profilu
    else: # pokud metoda není post, přesměruje se uživatel na stránku s formulářem pro změnu e-mailu
        return render_template("profile_forms/email.html")
    
@app.route("/change_password", methods=["POST","GET"]) # route pro změnu hesla
def change_password():
    if request.method=="POST": # pokud je metoda post
        password=request.form["password"] # získání hesla z formuláře
        session["password"]=password # nastavení session["password"] na hodnotu získanou z formuláře
        cur, con = db_connect() 
        cur.execute("UPDATE user SET password=? WHERE username=?",(password,session["username"])) # aktualizace atributu password na hodnotu z formuláře pro záznamy, kde se password rovná session["password"]
        con.commit() # commitnutí výsledku dotazu do databáze
        return redirect(url_for("profile")) # přesměrování na funkci pro zobrazení uživatelského profilu
    else: # pokud metoda není post, přesměruje se uživatel na stránku s formulářem pro změnu hesla
        return render_template("profile_forms/password.html")
    
@app.route("/change_username", methods=["POST","GET"]) # route pro změnu už. jména
def change_username():
    if request.method=="POST": # pokud je metoda post
        username=request.form["username"] # získání už. jména z formuláře
        cur, con = db_connect()
        if session["username"]==username: # pokud se proměnná username rovná session["username"], nic se neudělá, protože by změna nic nezpůsobila
            pass
        else: # pokud je prázdná, dojde ke změně
            cur.execute("UPDATE user SET username=? WHERE username=?",(username,session["username"])) # aktualizace atributu username na hodnotu z formuláře pro záznamy, kde se username rovná session["username"]
            session["username"]=username # nastavení session["username"] na získanou hodnotu z formuláře
            con.commit() # commitnutí výsledku dotazu do databáze
            return redirect(url_for("profile")) # přesměrování na funkci pro zobrazení uživatelského profilu
    else: # pokud metoda není post, přesměruje se uživatel na stránku s formulářem pro změnu už. jména
        return render_template("profile_forms/username.html")

@app.route("/logout")
def logout():
    session.pop("username",None) # odebrání proměnné username ze session
    session.pop("password",None) # proměnné password
    session.pop("email",None) # proměnné e-mail
    session.pop("bio",None) # proměnné bio
    return redirect(url_for('index')) # přesměrování na funkci pro zobrazení hlavní stránky

if __name__=="__main__": # zajištění toho, že soubor app.py se spustí pouze tehdy, pokud bude spouštěn jako hlavní soubor a ne např. jen jako importovaný modul do jiného souboru
    app.run() # zapnutí proměnné app uvedené na začátku souboru
