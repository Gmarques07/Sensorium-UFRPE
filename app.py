import os
import re
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(_name_)
app.secret_key = os.urandom(24)

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'banco_de_dados'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

def encontrar_usuario(cpf):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE cpf = %s"
    cursor.execute(query, (cpf,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario

def encontrar_empresa(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM empresas WHERE email = %s"
    cursor.execute(query, (email,))
    empresa = cursor.fetchone()
    cursor.close()
    conn.close()
    return empresa

def editar_usuario(cpf, nome=None, email=None, endereco=None, senha=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE usuarios SET nome = %s, email = %s, endereco = %s, senha = %s WHERE cpf = %s"
    cursor.execute(query, (nome, email, endereco, senha, cpf))
    conn.commit()
    cursor.close()
    conn.close()

def editar_empresa(email, nome=None, endereco=None, telefone=None, senha=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE empresas SET nome = %s, endereco = %s, telefone = %s, senha = %s WHERE email = %s"
    cursor.execute(query, (nome, endereco, telefone, senha, email))
    conn.commit()
    cursor.close()
    conn.close()

def aceitar_pedido(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE pedidos SET status = 'aceito' WHERE id = %s"
    cursor.execute(query, (pedido_id,))
    conn.commit()
    cursor.close()
    conn.close()

def excluir_pedido(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM pedidos WHERE id = %s"
    cursor.execute(query, (pedido_id,))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def pagina_inicial():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e), 500

@app.route('/login_usuario', methods=['GET', 'POST'])
def login_usuario():
    try:
        if request.method == 'POST':
            cpf = request.form['cpf']
            senha = request.form['senha']
            usuario = encontrar_usuario(cpf)
            if usuario and usuario['senha'] == senha:
                session['usuario_id'] = usuario['id']
                session['nome_usuario'] = usuario['nome']
                session['cpf'] = cpf
                return redirect(url_for('dashboard_usuario', cpf=cpf))
            flash('CPF ou senha incorretos', 'danger')
            return redirect(url_for('login_usuario'))
        
        cadastro_sucesso = request.args.get('cadastro_sucesso')
        return render_template('login_usuario.html', cadastro_sucesso=cadastro_sucesso)
    except Exception as e:
        return str(e), 500

@app.route('/login_empresa', methods=['GET', 'POST'])
def login_empresa():
    try:
        if request.method == 'POST':
            email = request.form['email']
            senha = request.form['senha']
            empresa = encontrar_empresa(email)
            if empresa and empresa['senha'] == senha:
                session['empresa_id'] = empresa['id']
                session['nome_empresa'] = empresa['nome']
                return redirect(url_for('perfil_empresa', email=email))
            flash('Email ou senha incorretos', 'danger')
            return redirect(url_for('login_empresa'))
        return render_template('login_empresa.html')
    except Exception as e:
        return str(e), 500

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    try:
        if request.method == 'POST':
            nome = request.form['nome']
            cpf = request.form['cpf'].replace('.', '').replace('-', '')
            email = request.form['email']
            endereco = request.form['endereco']
            senha = request.form['senha']
            confirmacao_senha = request.form['confirmacao_senha']
            
            if senha != confirmacao_senha:
                flash('As senhas não coincidem', 'danger')
                return redirect(url_for('cadastro'))

            if not re.match(r'^\d{11}$', cpf):
                flash('O CPF deve conter apenas 11 dígitos numéricos', 'danger')
                return redirect(url_for('cadastro'))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO usuarios (nome, cpf, email, endereco, senha) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (nome, cpf, email, endereco, senha))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Cadastro realizado com sucesso', 'success')
            return redirect(url_for('login_usuario', cadastro_sucesso=True))
        
        return render_template('cadastro.html')
    except Exception as e:
        return str(e), 500
    
@app.route('/cadastro_empresa', methods=['GET', 'POST'])
def cadastro_empresa():
    try:
        if request.method == 'POST':
            nome_empresa = request.form['nome_empresa']
            cnpj = request.form['cnpj'].replace('.', '').replace('/', '').replace('-', '')
            email_empresa = request.form['email_empresa']
            senha_empresa = request.form['senha_empresa']
            confirmacao_senha_empresa = request.form['confirmacao_senha_empresa']
            
            if senha_empresa != confirmacao_senha_empresa:
                flash('As senhas não coincidem', 'danger')
                return redirect(url_for('cadastro_empresa'))

            if not re.match(r'^\d{14}$', cnpj):
                flash('O CNPJ deve conter apenas 14 dígitos numéricos', 'danger')
                return redirect(url_for('cadastro_empresa'))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO empresas (nome, cnpj, email, senha) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nome_empresa, cnpj, email_empresa, senha_empresa))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Cadastro realizado com sucesso. Faça o login abaixo.', 'success')
            return redirect(url_for('login_empresa'))
        
        return render_template('cadastro_empresa.html')
    except Exception as e:
        return str(e), 500

@app.route('/editar_usuario/<cpf>', methods=['GET', 'POST'])
def editar_usuario_perfil(cpf):
    try:
        usuario = encontrar_usuario(cpf)
        if not usuario:
            return "Usuário não encontrado", 404
        
        if request.method == 'POST':
            nome = request.form['nome']
            novo_cpf = request.form['cpf'].replace('.', '').replace('-', '')
            email = request.form['email']
            endereco = request.form['endereco']
            senha = request.form['senha']
            
            if not re.match(r'^\d{11}$', novo_cpf):
                flash('O CPF deve conter apenas 11 dígitos numéricos', 'danger')
                return redirect(url_for('editar_usuario_perfil', cpf=cpf))
            
            editar_usuario(cpf, nome, email, endereco, senha)
            flash('Perfil atualizado com sucesso', 'success')
            return redirect(url_for('login_usuario'))
        
        return render_template('editar_usuario.html', usuario=usuario)
    except Exception as e:
        return str(e), 500

@app.route('/editar_empresa/<email>', methods=['GET', 'POST'])
def editar_empresa_perfil(email):
    try:
        empresa = encontrar_empresa(email)
        if not empresa:
            return "Empresa não encontrada", 404
        
        if request.method == 'POST':
            nome = request.form['nome']
            endereco = request.form['endereco']
            telefone = request.form['telefone']
            senha = request.form['senha']
            editar_empresa(email, nome, endereco, telefone, senha)
            flash('Perfil atualizado com sucesso', 'success')
            return redirect(url_for('perfil_empresa', email=email))
        
        return render_template('editar_empresa.html', empresa=empresa)
    except Exception as e:
        return str(e), 500

@app.route('/perfil_empresa/<email>', methods=['GET'])
def perfil_empresa(email):
    try:
        if 'empresa_id' not in session:
            flash('Você deve estar logado para acessar esta página', 'warning')
            return redirect(url_for('login_empresa'))
        
        empresa = encontrar_empresa(email)
        if empresa:
            return render_template('perfil_empresa.html', empresa=empresa)
        else:
            return "Empresa não encontrada", 404
    except Exception as e:
        return str(e), 500

@app.route('/dashboard_usuario/<cpf>', methods=['GET'])
def dashboard_usuario(cpf):
    try:
        usuario = encontrar_usuario(cpf)
        if usuario:
            return render_template('dashboard_usuario.html', usuario=usuario)
        else:
            return "Usuário não encontrado", 404
    except Exception as e:
        return str(e), 500

@app.route('/solicitar_pedido', methods=['GET', 'POST'])
def solicitar_pedido():
    try:
        if request.method == 'POST':
            cpf = request.form['cpf']
            descricao = request.form['descricao']
            if not encontrar_usuario(cpf):
                flash('Usuário não encontrado', 'danger')
                return redirect(url_for('solicitar_pedido'))

            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO pedidos (cpf_usuario, descricao, status) VALUES (%s, %s, %s)"
            cursor.execute(query, (cpf, descricao, 'pendente'))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Pedido solicitado com sucesso', 'success')
            return redirect(url_for('dashboard_usuario', cpf=cpf))
        
        return render_template('solicitar_pedido.html')
    except Exception as e:
        return str(e), 500

@app.route('/aceitar_pedido/<int:pedido_id>')
def aceitar_pedido_view(pedido_id):
    try:
        aceitar_pedido(pedido_id)
        flash('Pedido aceito com sucesso', 'success')
        return redirect(url_for('perfil_empresa', email=session.get('nome_empresa')))
    except Exception as e:
        return str(e), 500

@app.route('/excluir_pedido/<int:pedido_id>')
def excluir_pedido_view(pedido_id):
    try:
        excluir_pedido(pedido_id)
        flash('Pedido excluído com sucesso', 'success')
        return redirect(url_for('perfil_empresa', email=session.get('nome_empresa')))
    except Exception as e:
        return str(e), 500

if _name_ == '_main_':
    app.run(debug=True)