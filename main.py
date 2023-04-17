from flask import Flask, render_template,request, redirect
import pymysql.cursors
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,login_required,login_user,current_user,logout_user


login_manager= LoginManager()


app= Flask(__name__)
login_manager.init_app(app)

app.config['SECRET_KEY']='kjsbkjfgabfjknbrgojajovnajov'

class User:
    def __init__(self,id,user,banned):
        self.is_authenticated = True
        self.is_anonymous= False
        self.is_active = not banned

        self.username=user
        self.id=id
    
    def get_id(self):
        return str(self.id)


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
    
    return User(result['id'],result['user'],result['ban'],)

@app.route("/")
def index(): 
    return render_template("meeptem.html.jinja")


@app.route("/feed", )
@login_required
def post_feed():
    cursor= connection.cursor()
    cursor.execute("SELECT * FROM `post` JOIN `users` ON `post` . `user_id` = `users`.`id` ORDER BY `timestamp` DESC;")
    results= cursor.fetchall()
    return render_template("feed.html.jinja", posts=results)

@app.route('/sign-in',methods=['POST','GET'])
def sign_in():
    if request.method == 'POST':
        cursor= connection.cursor()
        cursor.execute('SELECT * FROM `users` WHERE `user`= %s ',(request.form['username']))
        result= cursor.fetchone()

        if result is None:
            return redirect("/sign-in")
        
        if result['password']==(request.form['password']):
            user= User(result['id'],result['user'],result['ban'])

            login_user(user)

            return redirect('/feed')
        else:
            return render_template("sign_in.html.jinja")
        
    elif request.method=='GET':
        return render_template("sign_in.html.jinja")

        

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




@app.route('/profile/<username>')
def user_profile(username):
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM `users` WHERE `username`= %s",(username))

    return render_template("user_profile.html.jinja", user=result)



if __name__=='__main__':
    app.run(debug=True)

