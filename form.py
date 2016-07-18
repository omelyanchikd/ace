from flask_wtf import Form
from wtforms import TextField, TextAreaField
from wtforms.validators import Required


class AppForm(Form):
    steps = TextField('steps', validators=[Required()], default=10)
    firms = TextAreaField('firms', default='{"BasicFirm": 8,"IntuitiveFirm": 2}')
