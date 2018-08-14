from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import pymysql.cursors
import os
import bs4

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

localserver = True
app.secret_key = 'secret'

try:
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='kishan123',
                             db='Kish',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    blogpath = '/var/www/FlaskApp/FlaskApp/templates/content/blogposts'
    bookreviewpath = '/var/www/FlaskApp/FlaskApp/templates/content/bookreviews'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kishan123@localhost/Kish'
    db = SQLAlchemy(app)

except pymysql.err.OperationalError:
    print("database not stored locally, accessing database through remote connection")
    connection = pymysql.connect(host='139.59.228.125',
                                 user='root',
                                 password='kishan123',
                                 db='Kish',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    blogpath = 'templates/content/blogposts'
    bookreviewpath = 'templates/content/bookreviews'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:kishan123@139.59.228.125/Kish'
    db = SQLAlchemy(app)
    print("db did not work")



#https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory
bloglinks = []
bloglinks = os.listdir(blogpath)
blogtitles = []

bookreviewlinks = []
bookreviewlinks = os.listdir(bookreviewpath)
bookreviewtitles = []

for blog in bloglinks:
    exampleFile = open(blogpath+'/{}'.format(blog))
    exampleSoup = bs4.BeautifulSoup(exampleFile, "html5lib")
    test = exampleSoup.select('h2')
    test = test[0].getText()
    blogtitles.append(test)

for book in bookreviewlinks:
    exampleFile = open(bookreviewpath+'/{}'.format(book))
    exampleSoup = bs4.BeautifulSoup(exampleFile, "html.parser")
    test = exampleSoup.select('h2')
    test = test[0].getText()
    bookreviewtitles.append(test)

blogdict = dict(zip(bloglinks, blogtitles))
bookreviewdict = dict(zip(bookreviewlinks, bookreviewtitles))
# print(blogdict)


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
        cursor.close()

    return render_template('projects/booknotes.html', data=data, bookreviewdict = bookreviewdict)


@app.route('/chinese')
def chinese():
    return render_template('projects/chinese.html')


@app.route('/booknotes/<string:slug>', methods=['GET'])
def dynamic(slug):
    all_posts = Books.query.filter_by(slug=slug).all()
    length = len(all_posts)
    return render_template('bookpage.html',posts=all_posts,length=length)


@app.route('/blogs/<string:booklink>', methods=['GET'])
def dynamic1(booklink):
    return render_template('content/blogposts/{}'.format(booklink))\

@app.route('/bookreviews/<string:book>', methods=['GET'])
def dynamic2(book):
    return render_template('content/bookreviews/{}'.format(book))


@app.route('/exercises')
def exercises():
    return render_template('projects/exercises.html')


@app.route('/home', methods=["GET","POST"])
def home():
    books = Books.query.all()
    return render_template('home.html', books=books)


# @app.route('/edit/<string:sno>', methods=["GET","POST"])
# def edit(sno):
#     if request.method == 'POST':
#         title = request.form.get('title')
#         slug = request.form.get('slug')
#         note = request.form.get('note')
#         if sno == '0':
#             new_book = Books(title=title, slug=slug, note=note)
#             db.session.add(new_book)
#             db.session.commit()
#         else:
#             book = Books.query.filter_by(sno=sno).first()
#             book.title = title
#             print(book.title,title)
#             book.slug = slug
#             book.note = note
#             db.session.commit()
#         return redirect('/edit/'+sno)
#
#     book = Books.query.filter_by(sno=sno).first()
#     return render_template('edit.html',sno=sno,book=book)


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
    app.run(debug=True)
