from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

usuarios = []
empresas = []
pedidos = []


def encontrar_usuario(cpf):
    for usuario in usuarios:
        if usuario['cpf'] == cpf:
            return usuario
    return None

def encontrar_empresa(cnpj):
    for empresa in empresas:
        if empresa['cnpj'] == cnpj:
            return empresa
    return None

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
                return "CPF ou senha inválidos", 401
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
                return "email ou senha inválidos", 401
        return render_template('login_empresa.html')
    except Exception as e:
        return str(e), 500

@app.route('/cadastro', methods=['POST'])
def cadastro():
    try:
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email']
        endereco = request.form['endereco']
        senha = request.form['senha']
        if encontrar_usuario(cpf):
            return "Usuário já cadastrado", 400
        usuarios.append({
            'nome': nome,
            'cpf': cpf,
            'email': email,
            'endereco': endereco,
            'senha': senha
        })
        return redirect(url_for('login_usuario'))
    except Exception as e:
        return str(e), 500

@app.route('/perfil_empresa/<cnpj>')
def perfil_empresa(cnpj):
   try:
        empresa = encontrar_empresa(cnpj)
        if empresa:
            return render_template('perfil_empresa.html', empresa=empresa)
        return "Empresa não encontrada", 404
   except Exception as e:
        return str(e), 500

@app.route('/dashboard_usuario/<cpf>')
def dashboard_usuario(cpf):
   try:
        usuario = encontrar_usuario(cpf)
        if usuario:
            return render_template('dashboard_usuario.html', pedidos=pedidos)
        return "Usuário não encontrado", 404
   except Exception as e:
        return str(e), 500
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)