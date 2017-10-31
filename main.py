from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogzuse:blogzpassword@localhost:8889/blogzuse'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.static_folder = 'static'
app.secret_key = "y2kmlkcyklouisck"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
   
@app.route('/', methods=['GET'])
def index():
    blogger_list = User.query.all()
    return render_template('index.html', blogger_list=blogger_list)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    if request.args.get('id'):
       
        blog = Blog.query.filter_by(id=request.args.get('id')).first()
        return render_template('blogpost.html', blog=blog)
    
    elif request.args.get('user'):
       
        user = User.query.filter_by(id=request.args.get('user')).first()
        blogs = Blog.query.filter_by(owner=user).all()
        return render_template('blog.html', blog_posts=blogs, user=user)
          
    blog_posts = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', blog_posts=blog_posts, users=users)
    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    username = session['username']
    owner = User.query.filter_by(username=username).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        if blog_title == "":
            title_error = "The blog post must have a title!"
            return render_template('newpost.html',title_error=title_error)
        blog_content = request.form['form']
        if blog_content == "":
            content_error = "The blog post must have content!"
            return render_template('newpost.html',content_error=content_error)
        new_blog = Blog(title =blog_title, body =blog_content, owner = owner)
        db.session.add(new_blog)
        db.session.commit()
        new_blog_link = '/?id='+str(new_blog.id)
        return redirect(new_blog_link)

    return render_template('newpost.html')
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        user_error = ''
        password_error = ''
        verify_error = ''
        
        has_error = False
        
        if username == '':
            username_error = 'Username field is empty'
            return render_template('signup.html',username_error=username_error)
        elif len(username) < 3:
            username_error = 'Username is too short'
            return render_template('signup.html',username_error=username_error)
        elif username == existing_user:
            username_error = 'That name has already been taken'
            return render_template('signup.html',username_error=username_error)

        if password == '':
            password_error = 'Password field is empty'
            return render_template('signup.html',password_error=password_error)
        elif len(password) < 3:
            password_error = 'Password is too short (min:3)'
            return render_template('signup.html',password_error=password_error)
        elif password != verify:
            password_error = 'These fields do not match'
            return render_template('signup.html',password_error=password_error)
            verify_error = 'These fields do not match'
            return render_template('signup.html',verify_error=verify_error)
        
        if verify == '':
            verify_error = 'Please verify you typed your password correctly'
            return render_template('signup.html',verify_error=verify_error)
        
        
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')
        else:
            flash('Duplicate User')

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == '':
            flash('Error! No username or password filled in')
            return render_template('login.html')

        if user and user.password == password:
            session['username'] = username
            flash('Welcome back, ' + user.username)
            return redirect('/')
        else:    
            flash('Incorrect username or password')
            

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')


if __name__ == '__main__':
    app.run()