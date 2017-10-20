from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-blog:blogpassword@localhost:8889/build-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.static_folder = 'static'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    
    blog_id = request.args.get('id')
    
    if blog_id:
        blog_post = Blog.query.get(blog_id)
        return render_template('blogpost.html',blog_post=blog_post)

    return render_template('blog.html',title="Blog List", 
        blogs=blogs)

# Blog.query.filter_by(id=int(request.args.get('id'))).all()
@app.route('/newpost', methods=['POST', 'GET'])
def delete_task():

    if request.method == 'POST':
        blog_title = request.form['title']
        if blog_title == "":
            title_error = "The blog post must have a title!"
            return render_template('newpost.html',title_error=title_error)
        blog_content = request.form['form']
        if blog_content == "":
            content_error = "The blog post must have content!"
            return render_template('newpost.html',content_error=content_error)
        new_blog = Blog(title =blog_title, body =blog_content)
        db.session.add(new_blog)
        db.session.commit()
        new_blog_link = '/?id='+str(new_blog.id)
        return redirect(new_blog_link)

    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()