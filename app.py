import re
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
            
            if not re.match(r'^\d{11}$', cpf):
                return "O CPF deve conter apenas 11 dígitos numéricos", 400
            
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

@app.route('/editar_usuario/<cpf>', methods=['GET', 'POST'])
def editar_usuario_perfil(cpf):
    try:
        usuario = encontrar_usuario(cpf)
        if not usuario:
            return "Usuário não encontrado", 404
        
        if request.method == 'POST':
            nome = request.form['nome']
            novo_cpf = request.form['cpf']
            email = request.form['email']
            endereco = request.form['endereco']
            senha = request.form['senha']
            
            # Validação de CPF: apenas números
            if not re.match(r'^\d{11}$', novo_cpf):
                return "O CPF deve conter apenas 11 dígitos numéricos", 400
            
            editar_usuario(cpf, nome, email, endereco, senha)
            
            # Redirecionar para a tela de login após a atualização dos dados
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
            return redirect(url_for('perfil_empresa', email=email))
        
        return render_template('editar_empresa.html', empresa=empresa)
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

@app.route('/solicitar_pedido', methods=['GET', 'POST'])
def solicitar_pedido():
    try:
        if request.method == 'POST':
            return redirect(url_for('dashboard_usuario', cpf=request.form['cpf']))  
        return render_template('solicitar_pedido.html')
    except Exception as e:
        return str(e), 500

@app.route('/aceitar_pedido/<int:pedido_id>', methods=['POST'])
def aceitar_pedido_route(pedido_id):
    try:
        aceitar_pedido(pedido_id)
        return redirect(url_for('solicitar_pedido'))
    except Exception as e:
        return str(e), 500

@app.route('/excluir_pedido/<int:pedido_id>', methods=['POST'])
def excluir_pedido_route(pedido_id):
    try:
        excluir_pedido(pedido_id)
        return redirect(url_for('solicitar_pedido'))
    except Exception as e:
        return str(e), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
