'''
     Creates a database with three tables (book, author, category)
     in the current directory which models books.
     Each book can have a many authors and many categories,
     thus relations Book - Authors and Book - Categories have been
     set up as many to many.

     If the file 'data.sqlite' is not present in the current directory
     please run from a command line:

     >python
     >from models import db
     >db.create_all()
'''

from app import db

author_association = db.Table('author_association',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'))
)

category_association = db.Table('category_association',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

class Book(db.Model):

    __tablename__='book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    author = db.relationship('Author',secondary=author_association,backref=db.backref('books',lazy ='dynamic'))
    category = db.relationship('Category',secondary=category_association,backref=db.backref('books',lazy='dynamic'))

    def __init__(self,title,description):
        self.title = title
        self.description = description


class Author(db.Model):

    __tablename__='author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return f"{self.name}"

class Category(db.Model):

    __tablename__='category'
    id = db.Column(db.Integer,primary_key=True)
    category = db.Column(db.Text)
    #books = db.relationship('Book',backref='category',lazy='dynamic')

    def __init__(self,category):
        self.category = category

    def __repr__(self):
        return f"{self.category}"
