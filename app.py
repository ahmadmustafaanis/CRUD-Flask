from bs4 import BeautifulSoup
    
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.exceptions import HTTPException


app = Flask(__name__)

app.jinja_env.filters['zip'] = zip
app.jinja_env.add_extension('jinja2.ext.loopcontrols')


app.config['MYSQL_HOST']= '127.0.0.1'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB'] = 'FINAL_STACKOVERFLOW'

mysql = MySQL(app)




## ERROR HANDLING

@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("500_generic.html", e=e), 500



#Create
@app.route('/')
def index():
    return render_template('index.html', messages='Welcome to home page')  #change this index.html and remove input forms from it 


@app.route('/input/user', methods=['GET', 'POST'])
def add_user():
    if request.method == "POST":
        details = request.form
        firstName = details['fname']
        rep = int(details['rep'])
        noa = int(details['noa'])
        noq = int(details['noq'])
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO USERS(USER_NAME, USER_REPUTATION, USER_NO_OF_ANSWERS, USER_NO_OF_QUESTIONS) VALUES (%s, %s, %s, %s)", (firstName, rep, noa, noq ))
            mysql.connection.commit()
            cur.close()
        except Exception as E:
            print(E)
            return render_template('error.html', message=E) #if any error
        return render_template('index.html') #if no error
    return render_template('user.html', messages="Input for User")


@app.route('/input/question', methods=['GET', 'POST'])
def insert_question():
    if request.method == "POST":
        details = request.form
        question_desc = details['QuestionDescription']
        id_user = int(details['user_details'])

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO QUESTION(QUESTION_DESCRIPTION, USER_ID) VALUES (%s, %s)", (question_desc, id_user))
        mysql.connection.commit()
        cur.close()
        #return render_template('index.html')
        return redirect("http://127.0.0.1:5000", code=302)


    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT USER_NAME, USER_ID FROM USERS''')
        Users = cur.fetchall()

        user_id = list(map(lambda a: a[1], Users))
        user_name = list(map(lambda a: a[0], Users))

        cur.close()
    except Exception as E:
        return render_template('error.html', message=E)
    return render_template('question.html', messages="Input for Questions", available_users_id = user_id, available_users_name = user_name)


@app.route('/input/answer', methods=['GET', 'POST'])
def give_answer():
    if request.method == 'POST':
        details = request.form
        answer_description = details['AnswerDescription']
        id_user = int(details['user_details'])
        question_id = int(details['question_details'])

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO ANSWER(ANSWER_DESCRIPTION, USER_ID) VALUES (%s, %s)", (answer_description, id_user))
        mysql.connection.commit() # insert answer to generate it's id

        cur.execute('''SELECT ANSWER_NUMBER FROM ANSWER''')
        answer_id = cur.fetchall()
        
        answer_id = list(map(lambda a: a[0], answer_id))[-1]
        
        cur.execute("INSERT INTO QUESTION_ANSWER(Q_NUM, A_NUM) VALUES (%s, %s)",(question_id,answer_id ) )

        mysql.connection.commit()
        cur.close()
        return redirect("http://127.0.0.1:5000", code=302)


    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT USER_NAME, USER_ID FROM USERS''')
        users = cur.fetchall()

        user_id = list(map(lambda a: a[1], users))
        user_name = list(map(lambda a: a[0], users))

        cur.execute('''SELECT QUESTION_DESCRIPTION, QUESTION_NUMBER FROM QUESTION''')

        questions = cur.fetchall()
        ques_desc = list(map(lambda a: a[0], questions))
        ques_id = list(map(lambda a: a[1], questions))

        cur.close()
    except Exception as E:
        return render_template('error.html', message=E)

    return render_template('answer.html', messages="Give ANSWER", available_users_id = user_id, available_users_name = user_name, questions_desc = ques_desc, question_id = ques_id)


@app.route('/input/badge', methods = ['GET', 'POST'])
def add_badge():
    if request.method == 'POST':
        details = request.form

        name = details['name']
        category = details['category']
        desc = details['desc']
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO BADGE(BADGE_NAME, BADGE_DESCRIPTION, BADGE_CATEGORY) VALUES (%s, %s, %s)", (name, desc, category))
            
            mysql.connection.commit()
            cur.close()
        except Exception as E:
            print("Sorry Error occured")
        return redirect(url_for('index'), code=302)
    
    return render_template('badge.html', message='Add new Badge')


#assign badge to user

@app.route('/input/user/assign_badge', methods=['GET', 'POST'])
def assign_badge():
    if request.method == 'POST':
        details = request.form

        user_id = details['user_id']
        badge_id = details['badge_id']

        try:
            cur = mysql.connection.cursor()

            cur.execute("INSERT INTO USER_BADGE (U_ID, B_ID) VALUES (%s, %s)", (user_id, badge_id))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('index'), code=302)
        except Exception as E:
            print("Sorry Error")
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT BADGE_ID, BADGE_NAME FROM BADGE")
        badge_det = cur.fetchall()
        badge_id = list(map(lambda a: a[0], badge_det))
        badge_name = list(map(lambda a: a[1], badge_det))
        print(badge_id)
        print(badge_name)
        cur.execute('''SELECT USER_NAME, USER_ID FROM USERS''')
        users = cur.fetchall()

        user_id = list(map(lambda a: a[1], users))
        user_name = list(map(lambda a: a[0], users))
        
        return render_template('user_badge.html', badge_id=badge_id, badge_name=badge_name, user_id=user_id, user_name=user_name)

        
    except Exception as E:
        print(E)




### READ OPERATIONS


@app.route('/read/questions', methods=['GET', 'POST'])
def read_questions():
    if request.method=='POST':
        details = request.form
        id = int(details['qid'])
        print(id )
        return redirect(url_for('answers_for_question', number=id))

    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT QUESTION_NUMBER, QUESTION_DESCRIPTION, VOTE_COUNT, QUESTION_VIEWS, USER_ID, QUESTION_NUMBER_OF_ANSWERS FROM QUESTION''')

    details = cur.fetchall()


    
    return render_template('read_questions.html', details=details)


    


@app.route('/read/question/<int:number>')
def answers_for_question(number):
    
    # try:
    cur = mysql.connection.cursor()
    cur.execute('''SELECT ANSWER.ANSWER_NUMBER, ANSWER.ANSWER_DESCRIPTION, QUESTION.QUESTION_NUMBER, QUESTION.QUESTION_DESCRIPTION FROM QUESTION INNER JOIN QUESTION_ANSWER ON QUESTION.QUESTION_NUMBER=QUESTION_ANSWER.Q_NUM INNER JOIN ANSWER ON ANSWER.ANSWER_NUMBER = QUESTION_ANSWER.A_NUM WHERE QUESTION.QUESTION_NUMBER=%s; ''', (number,))

    details = cur.fetchall()

    answer_number = list(map(lambda a:a[0], details))
    answer_desc = list(map(lambda a:a[1], details))



    #### CHANGE THIS LOGIC###################
    
    try:
        question_number = details[0][2]
        question_desc = details[0][3]
    ###################################

    except Exception as E:
        cur.execute('''SELECT QUESTION.QUESTION_NUMBER, QUESTION.QUESTION_DESCRIPTION FROM QUESTION''')
        details = cur.fetchall()
        print(details)
        question_number = list(map(lambda a:a[0], details))[-1]
        question_desc = list(map(lambda a:a[1], details))[-1]
        if question_number != number:
            return render_template('read_question_number.html', answer_number=None, answer_desc=None , question_desc='Question is Deleted', question_number=number)
    cur.close()
    return render_template('read_question_number.html', answer_number=answer_number, answer_desc=answer_desc, question_desc=question_desc, question_number=question_number)

@app.route('/read/user')
def user_details():
    cur = mysql.connection.cursor()

    cur.execute('''SELECT USERS.USER_ID, USERS.USER_NAME, USERS.USER_REPUTATION, USERS.USER_NO_OF_ANSWERS, USERS.USER_NO_OF_QUESTIONS, BADGE.BADGE_NAME, BADGE.BADGE_CATEGORY FROM USERS LEFT JOIN USER_BADGE ON USER_ID=USER_BADGE.U_ID LEFT JOIN BADGE ON BADGE.BADGE_ID = USER_BADGE.B_ID;''')

    details = cur.fetchall()
    uid = list(map(lambda a:a[0], details))

    
    uid = list(map(lambda a:a[0], details))
    uname = list(map(lambda a:a[1], details))
    urep = list(map(lambda a:a[2], details))
    unoa = list(map(lambda a:a[3], details))
    unoq = list(map(lambda a:a[4], details))





    return render_template('read_user.html', uid=uid, uname=uname, urep=urep, unoa=unoa, unoq=unoq, details=details)


@app.route('/read/badges', methods=['GET', 'POST'])
def badge_details():
    if request.method=='POST':
        details = request.form 
        uid = int(details['bid'])
        return redirect(url_for('single_badge', num=uid))
    cur = mysql.connection.cursor()

    cur.execute('''SELECT BADGE.BADGE_ID, BADGE.BADGE_NAME, USERS.USER_ID, USERS.USER_NAME FROM BADGE LEFT JOIN USER_BADGE ON BADGE.BADGE_ID = USER_BADGE.B_ID LEFT JOIN USERS ON USER_BADGE.U_ID=USERS.USER_ID''',)

    details = cur.fetchall()
    

    return render_template('read_badge.html', details=details)

@app.route('/read/badge/<int:num>')
def single_badge(num):
    cur = mysql.connection.cursor()

    cur.execute('''SELECT * FROM BADGE WHERE BADGE_ID=%s''', (num,))

    details = cur.fetchall()
    details = pd.DataFrame(list(details), columns=['ID', 'Name', 'Description', 'Category'])
    details.set_index(['ID', 'Name', 'Description', 'Category'], inplace=True)

    soup = BeautifulSoup(details.to_html(), features="lxml")
    soup.find("tr").extract()

    html = str(soup)
    print(html)
    return render_template('read_badge_num.html', tables=[html], det = details)


## UPDATE OPERATIONS

@app.route('/update/user', methods=['GET', 'POST'])
def update_user():
    if request.method=='POST':
        details = request.form 
        id = details.get('id')
        return redirect(url_for('update_user_no', no=id))
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM USERS''')
    details = cur.fetchall()
    uid = list(map(lambda a:a[0], details))
    uname = list(map(lambda a:a[1], details))
    rep = list(map(lambda a:a[2], details))
    noa = list(map(lambda a:a[3], details))
    noq = list(map(lambda a:a[4], details))
    cur.close()

    return render_template('update_user.html', uid=uid, uname=uname, rep=rep, noa=noa, noq=noq)

@app.route('/update/user/<int:no>', methods=['GET', 'POST'])
def update_user_no(no):

    if request.method=='POST':    
        cur = mysql.connection.cursor()
        details = request.form
        uname = details['uname']
        urep = details['urep']
        unoa = details['noa']
        unoq = details['noq']
        cur.execute('''UPDATE USERS SET USER_NAME=%s,USER_REPUTATION=%s, USER_NO_OF_ANSWERS=%s, USER_NO_OF_QUESTIONS=%s WHERE USER_ID=%s ''', (uname, urep, unoa, unoq, no))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('update_user'))

    return render_template('update_single_user.html')


@app.route('/update/badge', methods=['GET', 'POST'])
def get_badge_to_update():
    if request.method=='POST':
        details = request.form 
        id = details.get('id')
        return redirect(url_for('update_badge_no', no=id))
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM BADGE''')
    details = cur.fetchall()
    bid = list(map(lambda a:a[0], details))
    bname = list(map(lambda a:a[1], details))
    desc = list(map(lambda a:a[2], details))
    cat = list(map(lambda a:a[3], details))
    cur.close()

    return render_template('update_badge.html', bid=bid, bname=bname, desc=desc, cat=cat)

@app.route('/update/badge/<int:no>', methods=['GET', 'POST'])
def update_badge_no(no):
    if request.method=='POST':    
        cur = mysql.connection.cursor()
        details = request.form
        bname = details['bname']
        cat = details['cat']
        desc = details['desc']
        cur.execute('''UPDATE BADGE SET BADGE_NAME=%s, BADGE_DESCRIPTION=%s, BADGE_CATEGORY=%s WHERE BADGE_ID=%s ''', (bname, desc, cat, no))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('get_badge_to_update'))

    return render_template('update_badge_single.html')



@app.route('/update/question', methods=['GET','POST'])
def get_question_to_update():
    if request.method=='POST':
        details = request.form 
        id = details.get('id')
        return redirect(url_for('update_question_no', no=id))
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM QUESTION''')
    details = cur.fetchall()
    qno = list(map(lambda a:a[0], details))
    qdesc = list(map(lambda a:a[1], details))
    vote_count= list(map(lambda a:a[2], details))
    question_views = list(map(lambda a:a[3], details))
    user_id = list(map(lambda a:a[4], details))
    qnoa = list(map(lambda a:a[5], details))
    cur.close()

    return render_template('update_question.html', qno=qno, qdesc=qdesc, vc=vote_count, qviews=question_views, uid = user_id, qnoa=qnoa)


@app.route('/update/question/<int:no>', methods=['GET', 'POST'])
def update_question_no(no):
    if request.method=='POST':    
        cur = mysql.connection.cursor()
        details = request.form
        qdesc = details['qdesc']
        
        
        cur.execute('''UPDATE QUESTION SET QUESTION_DESCRIPTION=%s WHERE QUESTION_NUMBER=%s ''', (qdesc, no))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('get_question_to_update'))

    return render_template('update_question_single.html')



@app.route('/update/answer', methods=['GET','POST'])
def get_answer_to_update():
    if request.method=='POST':
        details = request.form 
        id = details.get('id')
        return redirect(url_for('update_answer_no', no=id))
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM ANSWER''')
    details = cur.fetchall()
    ano = list(map(lambda a:a[0], details))
    adesc = list(map(lambda a:a[3], details))
    vote_count= list(map(lambda a:a[1], details))
    isAccep = list(map(lambda a:a[2], details))
    user_id = list(map(lambda a:a[4], details))

    print(isAccep)
    isAccep = list(map(lambda a: 'Accepted' if a else 'Not Accepted', isAccep))
    
    cur.close()

    return render_template('update_answer.html', ano=ano, adesc=adesc, vc=vote_count, isAccep=isAccep, uid = user_id)


@app.route('/update/answer/<int:no>', methods=['GET', 'POST'])
def update_answer_no(no):
    if request.method=='POST':    
        cur = mysql.connection.cursor()
        details = request.form
        adesc = details['adesc']
        
        
        cur.execute('''UPDATE ANSWER SET ANSWER_DESCRIPTION=%s WHERE ANSWER_NUMBER=%s ''', (adesc, no))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('get_answer_to_update'))

    return render_template('update_answer_single.html')









### DELETE ROUTES

@app.route('/delete/user', methods=['GET', 'POST'])
def get_user_to_del():
    if request.method=='POST':
        details = request.form 
        uid = details['uid']

        cur = mysql.connection.cursor()

        cur.execute("DELETE FROM USERS WHERE USER_ID=%s", (uid,)) 

        mysql.connection.commit()
        cur.close()
        return render_template('success_deleted.html', message=f'user # {uid} deleted Successfully' )
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT USER_ID, USER_NAME FROM USERS''') #CHANGE QUERY

    details = cur.fetchall()

    uid = list(map(lambda a:a[0], details))
    uname = list(map(lambda a:a[1], details))

    return render_template('select_user_to_del.html', uid=uid, uname=uname) #CHANGE PAGE
    
    
## DELETE QUESTION

@app.route('/delete/question', methods=['GET', 'POST'])
def get_ques_to_del():
    if request.method=='POST':
        details = request.form 
        qid = details['qid']

        cur = mysql.connection.cursor()

        cur.execute("DELETE FROM QUESTION WHERE QUESTION_NUMBER=%s", (qid,)) 

        mysql.connection.commit()
        cur.close()
        return render_template('success_deleted.html', message=f'Question # {qid} deleted Successfully' )
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT QUESTION_NUMBER, QUESTION_DESCRIPTION FROM QUESTION''') 

    details = cur.fetchall()

    qid = list(map(lambda a:a[0], details))
    qdesc = list(map(lambda a:a[1], details))

    return render_template('select_question_to_del.html', qid=qid, qdesc=qdesc) 



#DELETE ANSWER
@app.route('/delete/answer', methods=['GET', 'POST'])
def get_ans_to_del():
    if request.method=='POST':
        details = request.form 
        aid = details['aid']

        cur = mysql.connection.cursor()

        cur.execute("DELETE FROM ANSWER WHERE ANSWER_NUMBER=%s", (aid,)) 
 
        mysql.connection.commit()
        cur.close()
        return render_template('success_deleted.html', message=f'ANSWER # {aid} deleted Successfully' )
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT ANSWER_NUMBER, ANSWER_DESCRIPTION FROM ANSWER''') 

    details = cur.fetchall()

    aid = list(map(lambda a:a[0], details))
    adesc = list(map(lambda a:a[1], details))

    return render_template('select_answer_to_del.html', aid=aid, adesc=adesc) 





#DELETE BADGE
@app.route('/delete/badge', methods=['GET', 'POST'])
def get_badge_to_del():
    if request.method=='POST':
        details = request.form 
        bid = details['bid']

        cur = mysql.connection.cursor()

        cur.execute("DELETE FROM BADGE WHERE BADGE_ID=%s", (bid,)) 

        mysql.connection.commit()
        cur.close()
        return render_template('success_deleted.html', message=f'BADGE # {bid} deleted Successfully' )
    
    cur = mysql.connection.cursor()
    cur.execute('''SELECT BADGE_ID, BADGE_NAME FROM BADGE''') 

    details = cur.fetchall()

    bid = list(map(lambda a:a[0], details))
    bname = list(map(lambda a:a[1], details))

    return render_template('select_badge_to_del.html', bid=bid, bname=bname) 

