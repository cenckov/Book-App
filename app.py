'''
Controller for a book app.

Author: Adam Cencek

'''


import os
import json
import requests
from forms import Filter, Google, New_Author, New_Category
from flask import render_template, redirect, url_for, request, flash
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

from models import *

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET','POST'])
def add():

    form_author = New_Author()
    form_category = New_Category()
    authors = Author.query.order_by(Author.name).all()
    categories = Category.query.order_by(Category.category).all()

    if request.method =='POST':

        if request.form.get('categoryadd') =="add":


            newcat = request.form.get('newcategory')
            category = Category.query.filter(func.lower(Category.category)==func.lower(f'{newcat}')).first()
            if category is None:
                newcat = Category(newcat)
                db.session.add(newcat)
                db.session.commit()
                return redirect(url_for('add'))
            else:
                 flash('Category already exists!')
                 return redirect(url_for('add'))

        elif request.form.get('authoradd') =="add":

             newaut = request.form.get('newauthor')
             author = Author.query.filter(func.lower(Author.name)==func.lower(f'{newaut}')).first()
             if author is None:
                 newaut = Author(newaut)
                 db.session.add(newaut)
                 db.session.commit()
                 return redirect(url_for('add'))
             else:
                 flash('Author already exists!')
                 return redirect(url_for('add'))


        elif request.form.get('addbook') =="save":

            title = request.form.get('title')
            description = request.form.get('description')
            authors = request.form.getlist('authors')
            categories = request.form.getlist('categories')

            newbook = Book(title,description)
            db.session.add(newbook)

            for author in authors:
                newbook.author.append(db.session.query(Author).get(int(author)))

            for category in categories:
                newbook.category.append(db.session.query(Category).get(int(category)))

            db.session.commit()
            return redirect(url_for('list'))

    return render_template('add_manual.html', authors = authors,categories=categories,
                            form_category=form_category,
                            form_author = form_author)

@app.route('/list',methods=['GET','POST'])
def list():
    form = Filter()

    if form.validate_on_submit():

        if form.search.data == '':
            books = Book.query.order_by(Book.title).all()
            return render_template('list.html', books=books, form =form)
        elif form.select.data == 'Author':
            books = Book.query.filter(Book.author.any(Author.name.like(f"%{form.search.data}%"))).order_by(Book.title).all()
            return render_template('list.html', books=books, form =form)
        elif form.select.data == 'Category':
            books = Book.query.filter(Book.category.any(Category.category.like(f"%{form.search.data}%"))).order_by(Book.title).all()
            return render_template('list.html', books=books, form =form)
        elif form.select.data == 'Title':
            books = Book.query.filter(Book.title.like(f"%{form.search.data}%")).order_by(Book.title).all()
            return render_template('list.html', books=books, form =form)

    elif request.method =='POST' and request.form.get('delete'):
        book = Book.query.get(int(request.form.get('delete')))
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('list'))

    books = Book.query.order_by(Book.title).all()
    return render_template('list.html', books=books, form =form)

@app.route('/google_books', methods=['GET','POST'])
def google_books():

    form = Google()

    if request.method =='POST' and form.search.data !='':
        return redirect(url_for('google_books_add',q=form.search.data,results=form.select.data))
    elif request.method =='POST' and form.search.data =='':
        flash('Please enter a keyword')

    return render_template('add_api.html',form=form)


@app.route('/google_books/add',methods=['GET','POST'])
def google_books_add():

    book = []
    books =[]
    q=request.args.get('q')
    results=request.args.get('results')

    payload = {'q': f'{q}','maxResults':f'{results}'}
    req = requests.get("https://www.googleapis.com/books/v1/volumes", params=payload)

    data = json.loads(req.text)

    try:
        num_of_books = len(data['items'])

        for i in range(num_of_books):
            try:
                book.append(data['items'][i]['volumeInfo']['title'])
            except KeyError:
                book.append('')
            try:
                book.append(data['items'][i]['volumeInfo']['authors'])
            except KeyError:
                book.append('')
            try:
                book.append(data['items'][i]['volumeInfo']['categories'])
            except KeyError:
                book.append('')
            try:
                book.append(data['items'][i]['volumeInfo']['description'])
            except KeyError:
                book.append('')
            books.append(book)
            book=[]
        for i in range(num_of_books):
            books[i].append(i)

    except KeyError:
        flash('No books found')

    if request.method=="POST":

        if request.form.get('addall'):

            for book in range(len(books)):
                new_book = Book(books[book][0],books[book][3])
                db.session.add(new_book)

                for author in books[book][1]:
                    authors = Author.query.filter_by(name=f'{author}').first()

                    if authors is None:
                        new = Author(author)
                        db.session.add(new)
                        new = Author.query.filter_by(name=f'{author}').first()
                        new_book.author.append(db.session.query(Author).get(int(new.id)))
                        db.session.commit()
                    else:
                        new = Author.query.filter_by(name=f'{author}').first()
                        new_book.author.append(db.session.query(Author).get(int(new.id)))
                        db.session.commit()

                for category in books[book][2]:
                    categories = Category.query.filter_by(category=f'{category}').first()

                    if categories is None:
                        new = Category(category)
                        db.session.add(new)
                        new = Category.query.filter_by(category=f'{category}').first()
                        new_book.category.append(db.session.query(Category).get(int(new.id)))
                        db.session.commit()
                    else:
                        new = Category.query.filter_by(category=f'{category}').first()
                        new_book.category.append(db.session.query(Category).get(int(new.id)))
                        db.session.commit()

                db.session.commit()

            return redirect(url_for('list'))

        else:
            book = int(request.form.get('add'))
            new_book = Book(books[book][0],books[book][3])
            db.session.add(new_book)

            for author in books[book][1]:
                authors = Author.query.filter_by(name=f'{author}').first()

                if authors is None:
                    new = Author(author)
                    db.session.add(new)
                    new = Author.query.filter_by(name=f'{author}').first()
                    new_book.author.append(db.session.query(Author).get(int(new.id)))
                    db.session.commit()
                else:
                    new = Author.query.filter_by(name=f'{author}').first()
                    new_book.author.append(db.session.query(Author).get(int(new.id)))
                    db.session.commit()

            for category in books[book][2]:
                categories = Category.query.filter_by(category=f'{category}').first()

                if categories is None:
                    new = Category(category)
                    db.session.add(new)
                    new = Category.query.filter_by(category=f'{category}').first()
                    new_book.category.append(db.session.query(Category).get(int(new.id)))
                    db.session.commit()
                else:
                    new = Category.query.filter_by(category=f'{category}').first()
                    new_book.category.append(db.session.query(Category).get(int(new.id)))
                    db.session.commit()

            return redirect(url_for('list'))

    return render_template('add_api_confirm.html',books=books)

@app.route('/admin',methods=['GET','POST'])
def admin():

    if request.method =='POST':

        db.engine.execute("delete from category_association;")
        db.engine.execute("delete from author_association;")
        Author.query.delete()
        Category.query.delete()
        Book.query.delete()
        db.session.commit()

        return redirect(url_for('list'))

    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=False)
