from flask import Flask, render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
from database import get_connection
from forms import RegisterForm, LoginForm, ClienteForm, ProdutoForm
import os
from config import SECRET_KEY
from functools import wraps
from uuid import UUID

# Decorador para proteger rotas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Faça login para acessar esta página!", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY  # Chave para segurança dos formulários

# Rota de Cadastro
@app.route('/register', methods=['GET', 'POST'])
@login_required
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
@login_required
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

# Rota de Cadastro_Produtos
@app.route('/cadastro_produtos', methods=['GET','POST'])
@login_required
def criar_produto():
    form = ProdutoForm()
    if form.validate_on_submit():
        nome = form.nome.data
        descricao = form.descricao.data
        quantidade = form.quantidade.data
        valor = form.valor.data

        conn = get_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES (%s, %s, %s, %s)",
                    (nome, descricao, quantidade, valor)
                )
                conn.commit()
                flash("Cadastro realizado com sucesso!", "success")
                return redirect(url_for('login'))
            except psycopg2.IntegrityError:
                flash("Produto já cadastrado!", "danger")
            finally:
                cur.close()
                conn.close()
    return render_template('cadastro_produtos.html', form=form)


# Rota para listar todos os clientes cadastrados
@app.route('/clientes')
@login_required
def listar_clientes():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nome, email, telefone, endereco FROM clientes")
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/produtos')
@login_required
def listar_produtos():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nome, descricao, preco, quantidade_estoque FROM produtos")
    produtos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('produtos.html', produtos=produtos)

# Rota para editar produto
@app.route('/produtos/editar/<uuid:id>', methods=['PUT'])
def editar_produto(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Usando request.form.get() para obter os dados
    nome = request.form.get('produto_nome')
    descricao = request.form.get('produto_descricao')
    quantidade = request.form.get('produto_quantidade')
    preco = request.form.get('produto_preco')

    try:
        preco = float(preco) if preco else None
    except ValueError:
        preco = None

    try:
        quantidade = int(quantidade) if quantidade else None
    except ValueError:
        quantidade = None

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE produtos SET nome = %s, descricao = %s, preco = %s, quantidade_estoque = %s WHERE id = %s",
            (nome, descricao, preco, quantidade, str(id))  # Converte UUID para string
        )
        conn.commit()
        return "Produto atualizado com sucesso", 200
    except Exception as e:
        print("Erro ao editar produto:", e)
        return f"Erro ao atualizar produto: {e}", 500
    finally:
        cur.close()
        conn.close()



# Rota para excluir produto
@app.route('/produtos/excluir/<uuid:id>', methods=['DELETE'])
def excluir_produto(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM produtos WHERE id = %s", (str(id),))  # Converte UUID para string
        conn.commit()
        return "Produto excluído com sucesso", 200
    except Exception as e:
        print("Erro ao excluir produto:", e)
        return "Erro ao excluir produto", 500
    finally:
        cur.close()
        conn.close()

# Rota para editar cliente
@app.route('/clientes/editar/<uuid:id>', methods=['POST'])
def editar_cliente(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    nome = request.form.get('cliente_nome')
    email = request.form.get('cliente_email')
    telefone = request.form.get('cliente_telefone')
    endereco = request.form.get('cliente_endereco')

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE clientes SET nome = %s, email = %s, telefone = %s, endereco = %s WHERE id = %s",
            (nome, email, telefone, endereco, str(id))  # Converte UUID para string
        )
        conn.commit()
        return "Cliente atualizado com sucesso", 200
    except Exception as e:
        print("Erro ao editar cliente:", e)
        return "Erro ao atualizar cliente", 500
    finally:
        cur.close()
        conn.close()

# Rota de Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta!", "info")
    return redirect(url_for('login'))

# Rota Protegida (Exemplo de Dashboard)
@app.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' not in session:
        flash("Faça login para acessar esta página!", "warning")
        return redirect(url_for('login'))
    return f"Bem-vindo, {session['user_name']}!"

if __name__ == '__main__':
    app.run(debug=True)