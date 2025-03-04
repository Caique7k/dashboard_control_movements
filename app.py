from flask import Flask, render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
from database import get_connection
from forms import RegisterForm, LoginForm, ClienteForm
import os
from config import SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY  # Chave para segurança dos formulários

# Rota de Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        senha_hash = generate_password_hash(form.senha.data)

        conn = get_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)",
                    (nome, email, senha_hash)
                )
                conn.commit()
                flash("Cadastro realizado com sucesso!", "success")
                return redirect(url_for('login'))
            except psycopg2.IntegrityError:
                flash("E-mail já cadastrado!", "danger")
            finally:
                cur.close()
                conn.close()
    return render_template('register.html', form=form)

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data

        conn = get_connection()
        if conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user and check_password_hash(user['senha_hash'], senha):
                session['user_id'] = user['id']
                session['user_name'] = user['nome']
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("E-mail ou senha incorretos!", "danger")
    return render_template('login.html', form=form)

# Rota de Cadastro_Clientes
@app.route('/cadastro_clientes', methods=['GET','POST'])
def criar_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        telefone = form.telefone.data
        endereco = form.endereco.data

        conn = get_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO clientes (nome, email, telefone, endereco) VALUES (%s, %s, %s, %s)",
                    (nome, email, telefone, endereco)
                )
                conn.commit()
                flash("Cadastro realizado com sucesso!", "success")
                return redirect(url_for('login'))
            except psycopg2.IntegrityError:
                flash("E-mail já cadastrado!", "danger")
            finally:
                cur.close()
                conn.close()
    return render_template('cadastro_clientes.html', form=form)

# Rota de Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta!", "info")
    return redirect(url_for('login'))

# Rota Protegida (Exemplo de Dashboard)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Faça login para acessar esta página!", "warning")
        return redirect(url_for('login'))
    return f"Bem-vindo, {session['user_name']}!"

if __name__ == '__main__':
    app.run(debug=True)