from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import pymysql.cursors
import os
import bs4

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

localserver = False
app.secret_key = 'secret'


if (localserver):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/kish'
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='kish',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    db = SQLAlchemy(app)
    blogpath = 'templates/blogposts'

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kishan123@localhost/Kish'
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='kishan123',
                             db='Kish',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    db = SQLAlchemy(app)
    blogpath = '/var/www/FlaskApp/FlaskApp/templates/blogposts'

#https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory
bloglinks = []
bloglinks = os.listdir(blogpath)
blogtitles = []

for blog in bloglinks:
    exampleFile = open(blogpath+'/{}'.format(blog))
    exampleSoup = bs4.BeautifulSoup(exampleFile, "html")
    test = exampleSoup.select('h2')
    test = test[0].getText()
    blogtitles.append(test)

blogdict = dict(zip(bloglinks, blogtitles))
print(blogdict)


class Books(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    note = db.Column(db.Text)
    slug = db.Column(db.String(20))

@app.route('/')
def hello_world():
    #sample route to show how route can push variables to template,
    #template does not actually use these arguments.
    author = "Me"
    name = "You"
    return render_template('index.html', author=author, name=name, blogtitles=blogtitles, bloglinks=bloglinks,
                           blogdict=blogdict)


@app.route('/booknotes')
def booknotes():

    with connection.cursor() as cursor:
        sql = "SELECT DISTINCT title,slug FROM `books` ORDER BY slug"
        cursor.execute(sql)
        data = cursor.fetchall()

    return render_template('projects/booknotes.html',data=data)


@app.route('/chinese')
def chinese():
    return render_template('projects/chinese.html')


@app.route('/mindmap')
def mindmap():
    return render_template('projects/mindmap.html')


@app.route('/booknotes/<string:slug>', methods=['GET'])
def dynamic(slug):
    all_posts = Books.query.filter_by(slug=slug).all()
    length = len(all_posts)
    return render_template('bookpage.html',posts=all_posts,length=length)


@app.route('/blogs/<string:booklink>', methods=['GET'])
def dynamic1(booklink):
    return render_template('blogposts/{}'.format(booklink))


@app.route('/exercises')
def exercises():
    return render_template('projects/exercises.html')


@app.route('/home', methods=["GET","POST"])
def home():
    books = Books.query.all()
    return render_template('home.html', books=books)


@app.route('/edit/<string:sno>', methods=["GET","POST"])
def edit(sno):
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        note = request.form.get('note')
        if sno == '0':
            new_book = Books(title=title, slug=slug, note=note)
            db.session.add(new_book)
            db.session.commit()
        else:
            book = Books.query.filter_by(sno=sno).first()
            book.title = title
            print(book.title,title)
            book.slug = slug
            book.note = note
            db.session.commit()
        return redirect('/edit/'+sno)

    book = Books.query.filter_by(sno=sno).first()
    return render_template('edit.html',sno=sno,book=book)


@app.route('/post1', methods=["GET", "POST"])
def post1():
    return render_template('blogposts/post1.html')


@app.route('/post2', methods=["GET", "POST"])
def post2():
    return render_template('blogposts/post2.html')


@app.route('/post3', methods=["GET", "POST"])
def post3():
    return render_template('blogposts/post3.html')


if __name__ == "__main__":
    app.run()