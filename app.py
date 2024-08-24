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
    return render_template('index.html')

@app.route('/login_usuario', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']
        usuario = encontrar_usuario(cpf)
        if usuario and usuario['senha'] == senha:
            return redirect(url_for('dashboard_usuario', cpf=cpf))
        else:
            return "CPF ou senha inválidos", 401
    return render_template('login_usuario.html')

@app.route('/login_empresa', methods=['GET', 'POST'])
def login_empresa():
    if request.method == 'POST':
        cnpj = request.form['cnpj']
        senha = request.form['senha']
        empresa = encontrar_empresa(cnpj)
        if empresa and empresa['senha'] == senha:
            return redirect(url_for('perfil_empresa', cnpj=cnpj))
        else:
            return "CNPJ ou senha inválidos", 401
    return render_template('login_empresa.html')

@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form['nome']
    cpf = request.form['cpf']
    email = request.form['email']
    endereco = request.form['endereco']
    senha = request.form['senha']
    usuarios.append({
        'nome': nome,
        'cpf': cpf,
        'email': email,
        'endereco': endereco,
        'senha': senha
    })
    return redirect(url_for('login_usuario'))

@app.route('/perfil_empresa/<cnpj>')
def perfil_empresa(cnpj):
    empresa = encontrar_empresa(cnpj)
    if empresa:
        return render_template('perfil_empresa.html', empresa=empresa)
    return "Empresa não encontrada", 404

@app.route('/dashboard_usuario/<cpf>')
def dashboard_usuario(cpf):
    usuario = encontrar_usuario(cpf)
    if usuario:
        return render_template('dashboard_usuario.html', pedidos=pedidos)
    return "Usuário não encontrado", 404

if __name__ == '__main__':
    app.run(debug=True)
