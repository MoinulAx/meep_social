from flask import Flask, render_template,request, redirect
import pymysql.cursors
import pymysql
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager

login_manager= LoginManager


app= Flask(__name__)
auth = HTTPBasicAuth()

login_manager.init_app(app)

class User:
    def __init__(self,id,user,banned):
        self.is_authenticated = True
        self.is_anonymous= False
        self.is_active = not banned

        self.username=user
        self.id=id
    
    def get_id(self):
        return str(self.id)

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

@login_manager.user_loader
def user_loader(user_id):
    cursor= connection.cursor()

    cursor.execute("SELECT * from `users` WHERE `id` = "+user_id)

    result = cursor.fetchone()

    if result is None:
        return None
    
    return User(result['id'],result['user'],result['banned'],)

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

        Avatar = request.files['Avatar']
        file_name=Avatar.filename
        file_extension=file_name.split('.')[-1]
        if file_extension in ['jpg','jpeg','png','gif']:
            Avatar.save('media/users/' +file_name)
        else:
            raise Exception('Invaild file type')


        cursor.execute("""
            INSERT INTO `users` (`user`,`password`,`Email`,`Bio`,`display_name`,`avatar`)
            VALUES (%s,%s,%s,%s,%s,%s)
        """,(request.form['username'],request.form['password'],request.form['email'],request.form['bio'],request.form['displayname'],file_name))
        return redirect("/feed")
    
    elif request.method == 'GET':
        return render_template("sign_up.html.jinja")    


if __name__=='__main__':
    app.run(debug=True)