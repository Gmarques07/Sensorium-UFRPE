import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'banco_de_dados_teste'
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
                return redirect(url_for('dashboard_usuario', cpf=cpf))
            else:
                return "CPF ou senha incorretos", 400
        return render_template('login_usuario.html')
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
                return redirect(url_for('perfil_empresa', email=email))
            else:
                return "Email ou senha incorretos", 400
        return render_template('login_empresa.html')
    except Exception as e:
        return str(e), 500


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    try:
        if request.method == 'POST':
            nome = request.form['nome']
            cpf = request.form['cpf']
            email = request.form['email']
            endereco = request.form['endereco']
            senha = request.form['senha']
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO usuarios (nome, cpf, email, endereco, senha) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (nome, cpf, email, endereco, senha))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('pagina_inicial'))
        return render_template('cadastro.html')
    except Exception as e:
        return str(e), 500


@app.route('/perfil_empresa/<email>', methods=['GET'])
def perfil_empresa(email):
    try:
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == '_main_':
    app.run(debug=True)