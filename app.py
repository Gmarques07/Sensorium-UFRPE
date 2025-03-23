import os
import re
import mysql.connector
from datetime import datetime
from flask import Flask, jsonify, request, session, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from time import time

app = Flask(__name__)
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

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_cracks(image):
    """Processa a imagem para detectar rachaduras."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cracks_found = False
    for contour in contours:
        if cv2.contourArea(contour) > 50:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h != 0 else 0
            
            perimeter = cv2.arcLength(contour, True)
            area = cv2.contourArea(contour)
            compactness = (perimeter ** 2) / (4 * np.pi * area) if area != 0 else 0

            if aspect_ratio > 5 or compactness > 10: 
                cv2.drawContours(image, [contour], -1, (0, 255, 0), 2) 
                cracks_found = True
    
    return image, cracks_found

def detect_objects(image):
    """Detecta objetos na imagem e desenha retângulos ao redor deles."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    _, threshold = cv2.threshold(blurred, 120, 255, cv2.THRESH_BINARY_INV)
    
    kernel = np.ones((3, 3), np.uint8)
    threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=2)
    threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    objects_found = False
    for contour in contours:
        area = cv2.contourArea(contour)
        if 500 < area < 10000:  
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h != 0 else 0
            perimeter = cv2.arcLength(contour, True)
            compactness = (perimeter ** 2) / (4 * np.pi * area) if area != 0 else 0
            
            if aspect_ratio < 5 and compactness < 10:  
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(image, "Objeto", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                objects_found = True
    
    return image, objects_found

def detect_cracks_or_objects(image):
    """Detecta rachaduras ou objetos na imagem."""
    processed_image_objects, objects_found = detect_objects(image.copy())
    processed_image_cracks, cracks_found = detect_cracks(image.copy())
    
    if cracks_found:
        return processed_image_cracks, "rachadura"
    elif objects_found:
        return processed_image_objects, "objeto"
    else:
        return image.copy(), "nenhum"
    
def salvar_imagem_pedido(pedido_id, tipo_imagem, caminho_imagem, tem_rachadura):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO imagens_pedido (pedido_id, tipo_imagem, caminho, tem_rachadura) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (pedido_id, tipo_imagem, caminho_imagem, tem_rachadura))
    conn.commit()
    cursor.close()
    conn.close()

def excluir_imagem(imagem_id):
    """Exclui uma imagem do banco de dados e do sistema de arquivos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT caminho FROM imagens_pedido WHERE id = %s"
        cursor.execute(query, (imagem_id,))
        imagem = cursor.fetchone()
        
        if not imagem:
            cursor.close()
            conn.close()
            return False
            
        query_delete = "DELETE FROM imagens_pedido WHERE id = %s"
        cursor.execute(query_delete, (imagem_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        caminho_completo = os.path.join('static', imagem['caminho'])
        if os.path.exists(caminho_completo):
            os.remove(caminho_completo)
            
        return True
    except Exception as e:
        print(f"Erro ao excluir imagem: {e}")
        return False

def notificar_rachadura(pedido_id, imagem_id, mensagem):
    """Cria uma notificação para a empresa sobre rachaduras detectadas"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query_pedido = "SELECT cpf_usuario, descricao FROM pedidos WHERE id = %s"
        cursor.execute(query_pedido, (pedido_id,))
        pedido = cursor.fetchone()
        
        assunto = f"ALERTA: Rachaduras detectadas no pedido #{pedido_id}"
        mensagem_completa = f"{mensagem}\n\nPedido: {pedido['descricao']}\nImagem ID: {imagem_id}"
        
        query = "INSERT INTO comunicados_gerais (assunto, mensagem) VALUES (%s, %s)"
        cursor.execute(query, (assunto, mensagem_completa))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao notificar rachadura: {e}")
        return False

def buscar_imagens_rachaduras(cnpj):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT i.id, i.caminho, i.data_upload, i.tem_rachadura
    FROM imagens_pedido i
    JOIN pedidos p ON i.pedido_id = p.id
    JOIN empresas e ON p.cnpj_empresa = e.cnpj
    WHERE e.cnpj = %s AND i.tipo_imagem = 'rachadura'
    ORDER BY i.data_upload DESC
    LIMIT 6
    """
    cursor.execute(query, (cnpj,))
    imagens = cursor.fetchall()
    cursor.close()
    conn.close()
    return imagens

def alterar_status_pedido(pedido_id, novo_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if novo_status not in ['pendente', 'aceito', 'cancelado']:
        raise ValueError("Status inválido")
    
    query = "UPDATE pedidos SET status = %s WHERE id = %s"
    cursor.execute(query, (novo_status, pedido_id))
    conn.commit()
    cursor.close()
    conn.close()


def encontrar_usuario(cpf):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE cpf = %s"
    cursor.execute(query, (cpf,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario

def encontrar_empresa(cnpj):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM empresas WHERE cnpj = %s"
    cursor.execute(query, (cnpj,))
    empresa = cursor.fetchone()
    cursor.close()
    conn.close()
    return empresa

def limpar_cnpj(cnpj):
    return re.sub(r'\D', '', cnpj) 

def editar_usuario(cpf_atual, nome=None, email=None, endereco=None, senha=None, novo_cpf=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if novo_cpf:
        query = "UPDATE usuarios SET cpf = %s WHERE cpf = %s"
        cursor.execute(query, (novo_cpf, cpf_atual))
        conn.commit()  
        cpf_atual = novo_cpf  

    if senha:
        query = "UPDATE usuarios SET nome = %s, email = %s, endereco = %s, senha = %s WHERE cpf = %s"
        cursor.execute(query, (nome, email, endereco, senha, cpf_atual))
    else:
        query = "UPDATE usuarios SET nome = %s, email = %s, endereco = %s WHERE cpf = %s"
        cursor.execute(query, (nome, email, endereco, cpf_atual))
    
    conn.commit()
    cursor.close()
    conn.close()

def editar_empresa(cnpj, nome=None, endereco=None, telefone=None, senha=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    set_values = []
    query = "UPDATE empresas SET "

    if nome:
        query += "nome = %s, "
        set_values.append(nome)
    if endereco:
        query += "endereco = %s, "
        set_values.append(endereco)
    if telefone:
        query += "telefone = %s, "
        set_values.append(telefone)
    if senha:
        query += "senha = %s, "
        set_values.append(senha)

    query = query.rstrip(', ') 

    query += " WHERE cnpj = %s"
    set_values.append(cnpj)

    cursor.execute(query, tuple(set_values))
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

def buscar_pedidos_usuarios(cpf):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT p.id, p.descricao, p.quantidade, p.data, p.status, u.nome AS usuario_nome
            FROM pedidos p
            JOIN usuarios u ON p.cpf_usuario = u.cpf
            WHERE p.cpf_usuario = %s
            ORDER BY p.data DESC
        """
        cursor.execute(query, (cpf,))
        pedidos = cursor.fetchall()
        cursor.close()
        conn.close()
        return pedidos
    except Exception as e:
        print(f"Erro ao buscar pedidos: {e}")
        return []

def buscar_todos_pedidos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome
            FROM pedidos p
            JOIN usuarios u ON p.cpf_usuario = u.cpf
            ORDER BY p.data DESC
        """
        cursor.execute(query)
        pedidos = cursor.fetchall()
        cursor.close()
        conn.close()
        return pedidos
    except Exception as e:
        print(f"Erro ao buscar todos os pedidos: {e}")
        return []

def enviar_comunicado_pedido(pedido_id, mensagem):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO comunicado_pedido (pedido_id, mensagem) VALUES (%s, %s)"
    cursor.execute(query, (pedido_id, mensagem))
    conn.commit()
    cursor.close()
    conn.close()

def buscar_comunicados_usuario(cpf):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT c.mensagem, c.data, c.lido
        FROM comunicado_pedido c
        JOIN pedidos p ON c.pedido_id = p.id
        WHERE p.cpf_usuario = %s
        ORDER BY c.data DESC
    """
    cursor.execute(query, (cpf,))
    comunicados = cursor.fetchall()
    cursor.close()
    conn.close()
    return comunicados

def buscar_comunicado_geral():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM comunicados_gerais ORDER BY data DESC"
    cursor.execute(query)
    comunicados = cursor.fetchall()
    cursor.close()
    conn.close()
    return comunicados

def enviar_comunicado_geral(assunto, mensagem):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO comunicados_gerais (assunto, mensagem) VALUES (%s, %s)"
    cursor.execute(query, (assunto, mensagem))
    conn.commit()
    cursor.close()
    conn.close()

def excluir_comunicado_geral(comunicado_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM comunicados_gerais WHERE id = %s"
    cursor.execute(query, (comunicado_id,))
    conn.commit()
    cursor.close()
    conn.close()

def buscar_dados_cisterna(cnpj):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query_ph_atual = "SELECT ph, data FROM ph_niveis ORDER BY data DESC LIMIT 1"
    cursor.execute(query_ph_atual)
    ph_atual = cursor.fetchone()
    
    query_historico_ph = "SELECT ph, data FROM ph_niveis ORDER BY data DESC LIMIT 10"
    cursor.execute(query_historico_ph)
    historico_ph = cursor.fetchall()
    
    query_nivel_atual = "SELECT boia, status, data FROM niveis_agua ORDER BY data DESC LIMIT 1"
    cursor.execute(query_nivel_atual)
    nivel_atual = cursor.fetchone()
    

    query_historico_nivel = "SELECT boia, status, data FROM niveis_agua ORDER BY data DESC LIMIT 10"
    cursor.execute(query_historico_nivel)
    historico_nivel = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return ph_atual, historico_ph, nivel_atual, historico_nivel

def criar_notificacao(pedido_id, mensagem):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO notificacoes (pedido_id, mensagem, data_criacao) VALUES (%s, %s, NOW())"
    cursor.execute(query, (pedido_id, mensagem))
    conn.commit()
    cursor.close()
    conn.close()

def buscar_notificacoes(cnpj):
    """
    Busca as notificações e as imagens processadas associadas aos pedidos da empresa.
    
    :param cnpj: CNPJ da empresa.
    :return: Lista de dicionários contendo notificações e imagens processadas.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query_notificacoes = """
        SELECT n.* 
        FROM notificacoes n
        JOIN pedidos p ON n.pedido_id = p.id
        WHERE p.cnpj_empresa = %s
        ORDER BY n.data_criacao DESC
        LIMIT 10
    """
    cursor.execute(query_notificacoes, (cnpj,))
    notificacoes = cursor.fetchall()
    
    for notificacao in notificacoes:
        query_imagens = """
            SELECT caminho, tipo_imagem, tem_rachadura
            FROM imagens_pedido
            WHERE pedido_id = %s
        """
        cursor.execute(query_imagens, (notificacao['pedido_id'],))
        notificacao['imagens'] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return notificacoes

def criar_pedido(cpf_usuario, descricao, quantidade, data, cnpj_empresa):
    conn = get_db_connection()
    cursor = conn.cursor()

    query_pedido = """
        INSERT INTO pedidos (cpf_usuario, descricao, quantidade, data, status, cnpj_empresa)
        VALUES (%s, %s, %s, %s, 'pendente', %s)
    """
    cursor.execute(query_pedido, (cpf_usuario, descricao, quantidade, data, cnpj_empresa))
    pedido_id = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()
    return pedido_id

def buscar_dados_cisterna_usuario(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query_ph_atual = "SELECT ph, data FROM ph_niveis WHERE usuario_id = %s ORDER BY data DESC LIMIT 1"
    cursor.execute(query_ph_atual, (usuario_id,))
    ph_atual = cursor.fetchone()
    
    query_historico_ph = "SELECT ph, data FROM ph_niveis WHERE usuario_id = %s ORDER BY data DESC LIMIT 10"
    cursor.execute(query_historico_ph, (usuario_id,))
    historico_ph = cursor.fetchall()
    

    query_nivel_atual = "SELECT boia, status, data FROM niveis_agua WHERE usuario_id = %s ORDER BY data DESC LIMIT 1"
    cursor.execute(query_nivel_atual, (usuario_id,))
    nivel_atual = cursor.fetchone()
    
    query_historico_nivel = "SELECT boia, status, data FROM niveis_agua WHERE usuario_id = %s ORDER BY data DESC LIMIT 10"
    cursor.execute(query_historico_nivel, (usuario_id,))
    historico_nivel = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return ph_atual, historico_ph, nivel_atual, historico_nivel

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
    if request.method == 'POST':
        cnpj = limpar_cnpj(request.form['cnpj'])
        senha = request.form['senha']
        empresa = encontrar_empresa(cnpj)

        if empresa and empresa['senha'] == senha:
            session['empresa_id'] = empresa['id']
            session['nome_empresa'] = empresa['nome']
            session['cnpj_empresa'] = empresa['cnpj']
            return redirect(url_for('perfil_empresa', cnpj=empresa['cnpj']))
        else:
            flash('CNPJ ou senha incorretos', 'danger')
            return redirect(url_for('login_empresa'))

    return render_template('login_empresa.html')

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
            query = "SELECT cpf FROM usuarios WHERE cpf = %s"
            cursor.execute(query, (cpf,))
            resultado = cursor.fetchone()

            if resultado:
                flash('CPF já cadastrado. Tente novamente com outro CPF.', 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('cadastro'))

            query = "INSERT INTO usuarios (nome, cpf, email, endereco, senha) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (nome, cpf, email, endereco, senha))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Cadastro realizado com sucesso', 'success')
            return redirect(url_for('login_usuario', cadastro_sucesso=True))

        return render_template('cadastro.html')
    except Exception as e:
        flash('Ocorreu um erro ao processar o cadastro. Tente novamente.', 'danger')
        return str(e), 500

@app.route('/cadastro_empresa', methods=['GET', 'POST'])
def cadastro_empresa():
    try:
        if request.method == 'POST':
            nome_empresa = request.form['nome_empresa']
            cnpj = request.form['cnpj'].replace('.', '').replace('/', '').replace('-', '')
            email_empresa = request.form['email_empresa']
            endereco_empresa = request.form['endereco_empresa']
            senha_empresa = request.form['senha_empresa']
            confirmacao_senha_empresa = request.form['confirmacao_senha_empresa']

            if not endereco_empresa.strip():
                flash('O endereço não pode estar vazio', 'danger')
                return redirect(url_for('cadastro_empresa'))

            if len(endereco_empresa) > 255:
                flash('O endereço é muito longo', 'danger')
                return redirect(url_for('cadastro_empresa'))

            if senha_empresa != confirmacao_senha_empresa:
                flash('As senhas não coincidem', 'danger')
                return redirect(url_for('cadastro_empresa'))

            if not re.match(r'^\d{14}$', cnpj):
                flash('O CNPJ deve conter apenas 14 dígitos numéricos', 'danger')
                return redirect(url_for('cadastro_empresa'))

            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT cnpj FROM empresas WHERE cnpj = %s"
            cursor.execute(query, (cnpj,))
            resultado = cursor.fetchone()

            if resultado:
                flash('CNPJ já cadastrado. Tente novamente com outro CNPJ.', 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('cadastro_empresa'))

            query = "INSERT INTO empresas (nome, cnpj, email, endereco, senha) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (nome_empresa, cnpj, email_empresa, endereco_empresa, senha_empresa))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Cadastro realizado com sucesso. Faça o login abaixo.', 'success')
            return redirect(url_for('login_empresa'))

        return render_template('cadastro_empresa.html')
    except Exception as e:
        flash('Ocorreu um erro ao processar o cadastro. Tente novamente.', 'danger')
        return str(e), 500

@app.route('/editar_usuario/<cpf>', methods=['GET', 'POST'])
def editar_usuario_perfil(cpf):
    try:
        usuario = encontrar_usuario(cpf)
        if not usuario:
            flash('Usuário não encontrado!', 'danger')
            return redirect(url_for('dashboard_usuario', cpf=cpf))

        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            endereco = request.form.get('endereco')
            senha = request.form.get('senha', None) 

            editar_usuario(cpf, nome, email, endereco, senha)  
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard_usuario', cpf=cpf)) 

        return render_template('editar_usuario.html', usuario=usuario)
    except Exception as e:
        return f"Erro interno: {str(e)}", 500


@app.route('/editar_empresa/<cnpj>', methods=['GET', 'POST'])
def editar_empresa_perfil(cnpj):
    try:
        empresa = encontrar_empresa(cnpj)
        if not empresa:
            return "Empresa não encontrada", 404

        if request.method == 'POST':
            nome = request.form['nome']
            endereco = request.form['endereco']
            senha = request.form['senha'] if 'senha' in request.form else None

            if not nome or not endereco:
                flash('Todos os campos são obrigatórios!', 'error')
                return redirect(request.url)

            if senha: 
                editar_empresa(cnpj, nome, endereco, senha)
            else: 
                editar_empresa(cnpj, nome, endereco)

            flash('Perfil atualizado com sucesso', 'success')
            return redirect(url_for('perfil_empresa', cnpj=cnpj))  

        return render_template('editar_empresa.html', empresa=empresa)

    except Exception as e:
        return str(e), 500


@app.route('/perfil_empresa/<cnpj>', methods=['GET'])
def perfil_empresa(cnpj):
    if 'empresa_id' not in session:
        flash('Você deve estar logado para acessar esta página', 'warning')
        return redirect(url_for('login_empresa'))

    empresa = encontrar_empresa(cnpj)
    pedidos = buscar_todos_pedidos()
    comunicados_gerais = buscar_comunicado_geral()

    if empresa:
        return render_template('perfil_empresa.html', empresa=empresa, pedidos=pedidos, comunicados_gerais=comunicados_gerais)
    else:
        return "Empresa não encontrada", 404

@app.route('/dashboard_usuario/<cpf>', methods=['GET'])
def dashboard_usuario(cpf):
    try:
        usuario = encontrar_usuario(cpf)
        if usuario:
            pedidos = buscar_pedidos_usuarios(cpf)
            comunicados = buscar_comunicados_usuario(cpf)
            comunicados_gerais = buscar_comunicado_geral()
            
            ph_atual, historico_ph, nivel_atual, historico_nivel = buscar_dados_cisterna_usuario(usuario['id'])
            
            return render_template('dashboard_usuario.html', 
                                   usuario=usuario, 
                                   pedidos=pedidos, 
                                   comunicados=comunicados, 
                                   comunicados_gerais=comunicados_gerais,
                                   ph_atual=ph_atual,
                                   nivel_atual=nivel_atual,
                                   historico_ph=historico_ph,
                                   historico_nivel=historico_nivel)
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
            quantidade = request.form['quantidade']
            data = request.form['data']
            cnpj_empresa = request.form['cnpj_empresa'] 

            if not descricao.strip():
                flash('A descrição não pode estar vazia', 'danger')
                return redirect(url_for('solicitar_pedido'))

            if not data:
                flash('A data de entrega é obrigatória', 'danger')
                return redirect(url_for('solicitar_pedido'))

            if int(quantidade) < 1000:
                flash('A quantidade mínima é 1000 litros', 'danger')
                return redirect(url_for('solicitar_pedido'))

            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO pedidos (cpf_usuario, descricao, quantidade, data, status, cnpj_empresa)
                VALUES (%s, %s, %s, %s, 'pendente', %s)
            """
            cursor.execute(query, (cpf, descricao, quantidade, data, cnpj_empresa))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Pedido solicitado com sucesso!', 'success')
            return redirect(url_for('dashboard_usuario', cpf=cpf))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT cnpj, nome FROM empresas"
        cursor.execute(query)
        empresas = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('solicitar_pedido.html', empresas=empresas)
    except Exception as e:
        flash(f'Ocorreu um erro ao processar o pedido: {str(e)}', 'danger')
        return redirect(url_for('solicitar_pedido'))

@app.route('/cancelar_pedido/<pedido_id>', methods=['POST'])
def cancelar_pedido(pedido_id):
    try:
        excluir_pedido(pedido_id)
        flash('Pedido cancelado com sucesso', 'success')
        return redirect(url_for('dashboard_usuario', cpf=session.get('cpf')))
    except Exception as e:
        return str(e), 500
    
@app.route('/excluir_pedido/<int:pedido_id>/<cnpj>', methods=['POST'])
def excluir_pedido_view(pedido_id, cnpj):
    excluir_pedido(pedido_id)
    flash('Pedido excluído com sucesso', 'success')
    return redirect(url_for('perfil_empresa', cnpj=cnpj))

@app.route('/alterar_status/<int:pedido_id>/<cnpj>', methods=['POST'])
def alterar_status(pedido_id, cnpj):
    novo_status = request.form['novo_status']
    alterar_status_pedido(pedido_id, novo_status)
    flash('Status do pedido alterado com sucesso', 'success')
    return redirect(url_for('perfil_empresa', cnpj=cnpj))

@app.route('/enviar_comunicado/<int:pedido_id>', methods=['POST'])
def enviar_comunicado_usuario(pedido_id):

    mensagem = request.form.get('mensagem')
    if not mensagem:
        flash('Mensagem não fornecida', 'error')
        return redirect(url_for('perfil_empresa', cnpj=session.get('cnpj_empresa')))
    
    enviar_comunicado_pedido(pedido_id, mensagem)
    flash('Comunicado enviado com sucesso', 'success') 
    
    return redirect(url_for('perfil_empresa', cnpj=session.get('cnpj_empresa')))

@app.route('/criar_comunicado', methods=['GET', 'POST'])
def criar_comunicado():
    if request.method == 'POST':
        assunto = request.form['assunto']
        mensagem = request.form['mensagem']
        enviar_comunicado_geral(assunto, mensagem)
        flash('Aviso enviado com sucesso!', 'success')

        cnpj_empresa = session.get('cnpj_empresa')
        if not cnpj_empresa:
            flash("Erro: Não foi possível identificar a empresa. Faça login novamente.", "danger")
            return redirect(url_for('login_empresa'))

        return redirect(url_for('perfil_empresa', cnpj=cnpj_empresa))

    return render_template('criar_comunicado.html')

@app.route('/excluir_comunicado_geral/<int:comunicado_id>', methods=['POST'])
def excluir_comunicado_geral_view(comunicado_id):
    excluir_comunicado_geral(comunicado_id)
    flash('Aviso excluído com sucesso', 'success')
    return redirect(url_for('perfil_empresa', cnpj=session.get('cnpj_empresa')))
    
@app.route('/pedido/<int:pedido_id>', methods=['GET'])
def visualizar_pedido(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query_pedido = """
        SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome
        FROM pedidos p
        JOIN usuarios u ON p.cpf_usuario = u.cpf
        WHERE p.id = %s
    """
    cursor.execute(query_pedido, (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        cursor.close()
        conn.close()
        return "Pedido não encontrado", 404

    query_imagens = """
        SELECT id, caminho, tipo_imagem, tem_rachadura
        FROM imagens_pedido
        WHERE pedido_id = %s
    """
    cursor.execute(query_imagens, (pedido_id,))
    imagens = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('pedido_detalhe.html', pedido=pedido, imagens=imagens)

@app.route('/detalhes_cisterna/<cnpj>')
def detalhes_cisterna(cnpj):
    empresa = encontrar_empresa(cnpj)
    if not empresa:
        return "Empresa não encontrada", 404

    ph_atual, historico_ph, nivel_atual, historico_nivel = buscar_dados_cisterna(cnpj)
    
    notificacoes = buscar_notificacoes(cnpj)
    
    return render_template(
        'detalhes_cisterna.html',
        empresa=empresa,
        ph_atual=ph_atual,
        historico_ph=historico_ph,
        nivel_atual=nivel_atual,
        historico_nivel=historico_nivel,
        notificacoes=notificacoes
    )
    
@app.route('/analisar_rachadura/<int:pedido_id>', methods=['POST'])
def analisar_rachadura(pedido_id):
    try:
        if 'imagem' not in request.files:
            flash('Nenhum arquivo enviado', 'danger')
            return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))
            
        file = request.files['imagem']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))

        if not allowed_file(file.filename):
            flash('Tipo de arquivo não permitido', 'danger')
            return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))

        filename = f"{int(time())}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        image = cv2.imread(filepath)
        if image is None:
            flash('Erro ao processar a imagem', 'danger')
            return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))

        processed_image, tipo_detectado = detect_cracks_or_objects(image)
        
        processed_filename = f"processed_{filename}"
        processed_filepath = os.path.join(app.config["UPLOAD_FOLDER"], processed_filename)
        cv2.imwrite(processed_filepath, processed_image)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        db_filepath = f"uploads/{processed_filename}"
        
        query = "INSERT INTO imagens_pedido (pedido_id, caminho, tipo_imagem, tem_rachadura) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (pedido_id, db_filepath, tipo_detectado, 1 if tipo_detectado == "rachadura" else 0))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        if tipo_detectado in ["rachadura", "objeto"]:
            mensagem = f"{tipo_detectado.capitalize()} detectado no pedido #{pedido_id}"
        else:
            mensagem = f"Imagem recebida para análise no pedido #{pedido_id}"
        criar_notificacao(pedido_id, mensagem)

        flash("Imagem enviada com sucesso! Será analisada pela empresa.", "success")
            
        os.remove(filepath)
            
        return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))
    except Exception as e:
        print(f"Erro ao analisar rachadura: {e}")
        flash(f"Erro ao processar a imagem: {str(e)}", 'danger')
        return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))
 
@app.route('/excluir_imagem/<int:imagem_id>/<int:pedido_id>', methods=['POST'])
def excluir_imagem_view(imagem_id, pedido_id):
    """Rota para excluir uma imagem"""
    try:
        if excluir_imagem(imagem_id):
            flash('Imagem excluída com sucesso', 'success')
        else:
            flash('Erro ao excluir imagem', 'danger')
    except Exception as e:
        flash(f'Erro ao excluir imagem: {str(e)}', 'danger')
        
    return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))

@app.route('/api/pedido/<int:pedido_id>')
def api_pedido(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome
        FROM pedidos p
        JOIN usuarios u ON p.cpf_usuario = u.cpf
        WHERE p.id = %s
    """
    cursor.execute(query, (pedido_id,))
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if pedido:
        
        pedido['data'] = pedido['data'].strftime('%Y-%m-%d %H:%M:%S') if pedido['data'] else None
        return jsonify(pedido)
    else:
        return jsonify({"error": "Pedido não encontrado"}), 404

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.template_filter('dateformat')
def dateformat(value, format="%d/%m/%Y %H:%M"):
    """Filtro para formatar datas no Jinja2"""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime(format)
    try:
        
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime(format)
    except ValueError:
        try:
            
            return datetime.strptime(value, "%Y-%m-%d").strftime(format)
        except:
            return value
        
@app.route('/informacoes_cisterna/<cpf>')
def informacoes_cisterna(cpf):
    usuario = encontrar_usuario(cpf)
    if not usuario:
        return "Usuário não encontrado", 404
    
    ph_atual, historico_ph, nivel_atual, historico_nivel = buscar_dados_cisterna(cpf)
    notificacoes = buscar_notificacoes(cpf)  
    
    return render_template('informacoes_cisterna.html', 
                           usuario=usuario,
                           ph_atual=ph_atual, 
                           historico_ph=historico_ph, 
                           nivel_atual=nivel_atual, 
                           historico_nivel=historico_nivel,
                           notificacoes=notificacoes)

@app.route('/rachaduras/<int:pedido_id>')
def rachaduras(pedido_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query_pedido = """
            SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome, p.cnpj_empresa
            FROM pedidos p
            JOIN usuarios u ON p.cpf_usuario = u.cpf
            WHERE p.id = %s
        """
        cursor.execute(query_pedido, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido:
            cursor.close()
            conn.close()
            return "Pedido não encontrado", 404
        
        query_imagens = """
            SELECT caminho, tipo_imagem, tem_rachadura
            FROM imagens_pedido
            WHERE pedido_id = %s
        """
        cursor.execute(query_imagens, (pedido_id,))
        imagens = cursor.fetchall()
        
        query_empresa = """
            SELECT cnpj, nome
            FROM empresas
            WHERE cnpj = %s
        """
        cursor.execute(query_empresa, (pedido['cnpj_empresa'],))
        empresa = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return render_template('rachaduras.html', pedido=pedido, imagens=imagens, empresa=empresa)
    except Exception as e:
        return str(e), 500
    
@app.route('/limpar_notificacao/<int:notificacao_id>', methods=['POST'])
def limpar_notificacao(notificacao_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Exclui a notificação específica
        query = "DELETE FROM notificacoes WHERE id = %s"
        cursor.execute(query, (notificacao_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Erro ao limpar notificação: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)