from flask import Flask, render_template,request, redirect,abort, send_from_directory
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

@app.get('/media/<path:path>')
def send_media(path):
    return send_from_directory('media', path)

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
        cursor.execute('SELECT * FROM `users` WHERE `user` = %s',(request.form['username']))
        result= cursor.fetchone()


        if result is None:
            return redirect("/sign-in")
        
        if result['password'] == request.form['password']:
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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html.jinja'), 404

@app.route('/profile/<username>')
def user_profile(username):
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM `users` WHERE `user`= %s",(username))

    result = cursor.fetchone()
    if result is None:
        abort(404)


    cursor.close()

    cursor=connection.cursor()

    cursor.execute("SELECT * from `post` WHERE `user_id`= %s",(result['id']))

    post_result= cursor.fetchall()

    return render_template("user_profile.html.jinja", user=result,posts=post_result)

@app.route('/post', methods=['POST'])
@login_required
def create_post():
    cursor = connection.cursor()

    photo = request.files['post_image']

    file_name = photo.filename # my_photo.jpg

    file_extension = file_name.split('.')[-1]

    if file_extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
        photo.save('media/posts/' + file_name)
    else:
        raise Exception('Invalid file type')

    user_id = current_user.id

    cursor.execute(
        "INSERT INTO `post` (`caption`, `post_image`, `user_id`) VALUES (%s, %s, %s)", 
        (request.form['post_text'], file_name, user_id)
    )

    return redirect('/feed')



if __name__=='__main__':
    app.run(debug=True)

