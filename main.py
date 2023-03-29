from flask import Flask, render_template,request, redirect
import pymysql.cursors
import pymysql
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app= Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "mkhan": generate_password_hash("1234"),
    "susan": generate_password_hash("susan")
}
@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


connection= pymysql.connect(
   
    host="10.100.33.60",
    user="mkhan",
    password='221085624',
    database='mkhan_meep_social',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True

)

@app.route("/")
def index(): 
    return render_template("meeptem.html.jinja")


@app.route("/feed")
def post_feed():
    cursor= connection.cursor()
    cursor.execute("SELECT * FROM `post` JOIN `users` ON `post` . `user_id` = `users`.`id` ORDER BY `timestamp` DESC;")
    results= cursor.fetchall()
    return render_template("feed.html.jinja", posts=results)

@app.route('/sign-in')
def sign_in(): 
    return render_template("sign_in.html.jinja")

@app.route('/sign-up',methods=['POST','GET'])
def sign_up():
    if request.method == 'POST':
    
        cursor=connection.cursor()
        cursor.execute("""
            INSERT INTO `users` (`user`,`password`,`Email`,`Bio`,`display_name`,`avatar`)
            VALUES (%s,%s,%s,%s,%s,%s)
        """,())
        return request.form
    
    elif request.method == 'GET':
        return render_template("sign_up.html.jinja")    


if __name__=='__main__':
    app.run(debug=True)