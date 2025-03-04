from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    submit = SubmitField('Registrar')

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ClienteForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    telefone = StringField('Telefone', validators=[DataRequired(), Length(min=8, max=20)])
    endereco = StringField('Endereço', validators=[DataRequired(), Length(min=3, max=200)])
    submit = SubmitField('Cadastrar')