from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def pagina_inicial():
    return render_template('index.html')

@app.route('/cadastro.html')
def cadastro():
    return render_template('cadastro.html')

@app.route('/login_usuario.html')
def login_usuario():
    return render_template('login_usuario.html')

@app.route('/login_empresa.html')
def login_empresa():
    return render_template('login_empresa.html')

@app.route('/processar_cadastro', methods=['POST'])
def processar_cadastro():
    nome = request.form['nome']
    cpf = request.form['cpf']
    email = request.form['email']
    endereco = request.form['endereco']
    senha = request.form['senha']
    # Aqui você pode adicionar a lógica para salvar os dados no banco de dados
    print(f'Cadastro de {nome} processado com sucesso!')
    return redirect('/')

@app.route('/login-usuario', methods=['POST'])
def login_usuario_processar():
    cpf = request.form['cpf']
    senha = request.form['senha']
    # Aqui você pode adicionar a lógica para verificar os dados de login
    print(f'Usuário com CPF {cpf} fez login.')
    return redirect('/')

@app.route('/login-empresa', methods=['POST'])
def login_empresa_processar():
    cnpj = request.form['cnpj']
    senha = request.form['senha']
    # Aqui você pode adicionar a lógica para verificar os dados de login
    print(f'Empresa com CNPJ {cnpj} fez login.')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
