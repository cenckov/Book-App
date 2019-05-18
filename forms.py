'''

Flask forms used in the project.

Filter       - filter bar on the books list page
New_Author   - new author form on the add page
New_Category - new author form on the add page
Google       - Google API search bar

'''

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, validators

class Filter(FlaskForm):

    choices = [('Author', 'Author'),
               ('Category', 'Category'),
               ('Title','Title')]
    select = SelectField('Filter by:', choices=choices)
    search = StringField('')
    submit = SubmitField('Search')

class New_Author(FlaskForm):

    author = StringField('New Author: ',[validators.DataRequired('Please enter author name')])
    submit = SubmitField('Add')

class New_Category(FlaskForm):

    category = StringField("New Category: ",[validators.DataRequired('Please enter category')])
    submit = SubmitField('Add')

class Google(FlaskForm):

    choices = [(1,1),(5,5),(10,10),(20,20),(30,30),(40,40)]
    select = SelectField('Number of Results:', choices=choices)
    search = StringField('',[validators.DataRequired('Please provide a keyword')])
    submit = SubmitField('Search')
