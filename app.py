import os
import re
import mysql.connector
from datetime import datetime
from flask import Flask, jsonify, request, session, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash 
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from time import time
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session
from flask import session, abort


app = Flask(__name__)
app.secret_key = os.urandom(24) 


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_usuario' 
login_manager.login_message = 'Você precisa estar logado para acessar esta página.'
login_manager.login_message_category = 'warning'

db_config = {
    'user': 'root',
    'password': 'osOvMtonkwxcbEphriXeJGPKdOxSfAzl',
    'host': 'ballast.proxy.rlwy.net',
    'port': 56724,
    'database': 'railway'
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


class Usuario(UserMixin):
    def __init__(self, id, cpf, nome, email, endereco, senha):
        self.id = id
        self.cpf = cpf
        self.nome = nome
        self.email = email
        self.endereco = endereco
        self.senha = senha 

    def get_id(self):
        return str(self.id)

    @staticmethod
    def from_db_row(row):

        if row:
            return Usuario(row['id'], row['cpf'], row['nome'], row['email'], row['endereco'], row['senha'])
        return None

    def is_a_usuario(self):
        return True
    def is_an_empresa(self):
        return False

class Empresa(UserMixin):
    def __init__(self, id, cnpj, nome, email, endereco, senha):
        self.id = id
        self.cnpj = cnpj
        self.nome = nome
        self.email = email
        self.endereco = endereco
        self.senha = senha 

    def get_id(self):
        return str(self.id)

    @staticmethod
    def from_db_row(row):
        if row:
            return Empresa(row['id'], row['cnpj'], row['nome'], row['email'], row['endereco'], row['senha'])
        return None

    def is_a_usuario(self):
        return False
    def is_an_empresa(self):
        return True
    
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    
    try:
        
        query_usuario = "SELECT id, cpf, nome, email, endereco, senha FROM usuarios WHERE id = %s"
        cursor.execute(query_usuario, (user_id,))
        usuario_data = cursor.fetchone()
        if usuario_data:
            return Usuario.from_db_row(usuario_data)

        
        query_empresa = "SELECT id, cnpj, nome, email, endereco, senha FROM empresas WHERE id = %s"
        cursor.execute(query_empresa, (user_id,))
        empresa_data = cursor.fetchone()
        if empresa_data:
            return Empresa.from_db_row(empresa_data)

        return None 
    except mysql.connector.Error as err:
        print(f"Erro no load_user: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def encontrar_usuario(cpf):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, cpf, nome, email, endereco, senha FROM usuarios WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        usuario = cursor.fetchone()
        return usuario
    except mysql.connector.Error as err:
        print(f"Erro ao buscar usuário: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def encontrar_empresa(cnpj):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, cnpj, nome, email, endereco, senha FROM empresas WHERE cnpj = %s"
        cursor.execute(query, (cnpj,))
        empresa = cursor.fetchone()
        return empresa
    except mysql.connector.Error as err:
        print(f"Erro ao buscar empresa: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def limpar_cnpj(cnpj):
    return re.sub(r'\D', '', cnpj) 

def editar_usuario(cpf_atual, nome=None, email=None, endereco=None, senha=None, novo_cpf=None):
    conn = get_db_connection()
    if not conn:
        return False 

    cursor = conn.cursor()

    try:
        
        if novo_cpf and novo_cpf != cpf_atual:
            query_update_cpf = "UPDATE usuarios SET cpf = %s WHERE cpf = %s"
            cursor.execute(query_update_cpf, (novo_cpf, cpf_atual))
            conn.commit()  
            cpf_atual = novo_cpf  

        update_fields = []
        update_values = []

        if nome is not None:
            update_fields.append("nome = %s")
            update_values.append(nome)
        if email is not None:
            update_fields.append("email = %s")
            update_values.append(email)
        if endereco is not None:
            update_fields.append("endereco = %s")
            update_values.append(endereco)
        
        if senha: 
            hashed_senha = generate_password_hash(senha)
            update_fields.append("senha = %s")
            update_values.append(hashed_senha)

        if update_fields:
            query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE cpf = %s"
            update_values.append(cpf_atual) 
            cursor.execute(query, tuple(update_values))
            conn.commit()
            return True 
        else:
            
            return True 
    except mysql.connector.Error as err:
        print(f"Erro ao editar usuário: {err}")
        conn.rollback() 
        return False 
    finally:
        if cursor:
            cursor.close()
        if conn:
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

def buscar_pedidos_por_empresa(cnpj):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome
            FROM pedidos p
            JOIN usuarios u ON p.cpf_usuario = u.cpf
            WHERE p.cnpj_empresa = %s
            ORDER BY p.data DESC
        """
        cursor.execute(query, (cnpj,))
        pedidos = cursor.fetchall()
        cursor.close()
        conn.close()
        return pedidos
    except Exception as e:
        print(f"Erro ao buscar pedidos por empresa: {e}")
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

def buscar_notificacoes(id_entidade):
    """
    Busca as notificações associadas a um ID de usuário ou empresa.
    Para empresa, buscará notificações de pedidos relacionados ao CNPJ.
    Para usuário, buscará notificações relacionadas ao CPF.
    
    :param id_entidade: ID do usuário ou CNPJ da empresa.
    :return: Lista de dicionários contendo notificações e imagens processadas.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    notificacoes = []

    if isinstance(id_entidade, str) and len(id_entidade) == 14:

        query_notificacoes = """
            SELECT n.* FROM notificacoes n
            JOIN pedidos p ON n.pedido_id = p.id
            WHERE p.cnpj_empresa = %s
            ORDER BY n.data_criacao DESC
            LIMIT 10
        """
        cursor.execute(query_notificacoes, (id_entidade,))
        notificacoes = cursor.fetchall()
        
        for notificacao in notificacoes:
            query_imagens = """
                SELECT caminho, tipo_imagem, tem_rachadura
                FROM imagens_pedido
                WHERE pedido_id = %s
            """
            cursor.execute(query_imagens, (notificacao['pedido_id'],))
            notificacao['imagens'] = cursor.fetchall()

    elif isinstance(id_entidade, int): 

        query_notificacoes = """
            SELECT n.* FROM notificacoes n
            JOIN pedidos p ON n.pedido_id = p.id
            JOIN usuarios u ON p.cpf_usuario = u.cpf
            WHERE u.id = %s
            ORDER BY n.data_criacao DESC
            LIMIT 10
        """
        cursor.execute(query_notificacoes, (id_entidade,))
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
            senha_digitada = request.form['senha']
            
            cpf_limpo = re.sub(r'\D', '', cpf)

            db_usuario_data = encontrar_usuario(cpf_limpo)
            
            usuario = Usuario.from_db_row(db_usuario_data)

            if usuario and check_password_hash(usuario.senha, senha_digitada):
                login_user(usuario) 
                flash(f'Bem-vindo(a), {usuario.nome}!', 'success')
                return redirect(url_for('dashboard_usuario', cpf=usuario.cpf))
            else:
                
                flash('CPF ou senha incorretos', 'danger')
                return redirect(url_for('login_usuario'))

        cadastro_sucesso = request.args.get('cadastro_sucesso')
        return render_template('login_usuario.html', cadastro_sucesso=cadastro_sucesso)
    except Exception as e:
        
        flash(f'Ocorreu um erro no login. Tente novamente.', 'danger')
        print(f"Erro detalhado no login_usuario: {e}") 
        return redirect(url_for('login_usuario'))

@app.route('/login_empresa', methods=['GET', 'POST'])
def login_empresa():
    try:
        if request.method == 'POST':
            cnpj = request.form['cnpj']
            senha_digitada = request.form['senha']
            
            cnpj_limpo = re.sub(r'\D', '', cnpj)

            db_empresa_data = encontrar_empresa(cnpj_limpo)
            empresa = Empresa.from_db_row(db_empresa_data)

            print(f"Tentativa de login para CNPJ: {cnpj_limpo}")
            print(f"Senha digitada: {senha_digitada}")
            
            if empresa:
                print(f"Empresa encontrada. Nome: {empresa.nome}")
                print(f"Hash da senha do DB (empresa.senha): {empresa.senha}")
                
                if empresa.senha is None or empresa.senha == "":
                    print("AVISO: Senha da empresa no banco de dados está vazia ou é None.")
                    flash('CNPJ ou senha incorretos', 'danger')
                    return redirect(url_for('login_empresa'))

                if check_password_hash(empresa.senha, senha_digitada):
                    login_user(empresa)
                    flash(f'Bem-vindo(a), {empresa.nome}!', 'success')
                    
                    return redirect(url_for('perfil_empresa', cnpj=empresa.cnpj))
                else:
                    print("check_password_hash retornou False. Senha não coincide.")
                    flash('CNPJ ou senha incorretos', 'danger')
                    return redirect(url_for('login_empresa'))
            else:
                print("Empresa não encontrada no banco de dados.")
                flash('CNPJ ou senha incorretos', 'danger')
                return redirect(url_for('login_empresa'))

        return render_template('login_empresa.html')
    except Exception as e:
        flash(f'Ocorreu um erro no login da empresa. Tente novamente.', 'danger')
        print(f"Erro detalhado no login_empresa: {e}")
        return redirect(url_for('login_empresa'))


@app.route('/logout')
@login_required 
def logout():
    logout_user() 
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('pagina_inicial'))

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
            if not conn: 
                return redirect(url_for('cadastro')) 
            
            cursor = conn.cursor()
            
            query_check_cpf = "SELECT cpf FROM usuarios WHERE cpf = %s"
            cursor.execute(query_check_cpf, (cpf,))
            resultado = cursor.fetchone()

            if resultado:
                flash('CPF já cadastrado. Tente novamente com outro CPF.', 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('cadastro'))
            
            hashed_senha = generate_password_hash(senha)

            query_insert_user = "INSERT INTO usuarios (nome, cpf, email, endereco, senha) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query_insert_user, (nome, cpf, email, endereco, hashed_senha)) 
            conn.commit()
            
            cursor.close()
            conn.close()

            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login_usuario', cadastro_sucesso=True))

        return render_template('cadastro.html')
    except Exception as e:
        flash('Ocorreu um erro ao processar o cadastro. Tente novamente.', 'danger')
        print(f"Erro no cadastro: {e}") 
        return redirect(url_for('cadastro')) 

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
            if not conn:
                return redirect(url_for('cadastro_empresa')) 
            
            cursor = conn.cursor()
            
            
            query_check_cnpj = "SELECT cnpj FROM empresas WHERE cnpj = %s"
            cursor.execute(query_check_cnpj, (cnpj,))
            resultado = cursor.fetchone()

            if resultado:
                flash('CNPJ já cadastrado. Tente novamente com outro CNPJ.', 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('cadastro_empresa'))
            
            
            hashed_senha_empresa = generate_password_hash(senha_empresa)
            
            query_insert_company = "INSERT INTO empresas (nome, cnpj, email, endereco, senha) VALUES (%s, %s, %s, %s, %s)"
            
            cursor.execute(query_insert_company, (nome_empresa, cnpj, email_empresa, endereco_empresa, hashed_senha_empresa))
            conn.commit()
            
            cursor.close()
            conn.close()

            flash('Cadastro realizado com sucesso. Faça o login abaixo.', 'success')
            return redirect(url_for('login_empresa'))

        return render_template('cadastro_empresa.html')
    except Exception as e:
        flash('Ocorreu um erro ao processar o cadastro. Tente novamente.', 'danger')
        print(f"Erro no cadastro_empresa: {e}") 
        return redirect(url_for('cadastro_empresa'))

@app.route('/editar_usuario/<cpf>', methods=['GET', 'POST'])
@login_required 
def editar_usuario_perfil(cpf):
    
    if not isinstance(current_user, Usuario) or current_user.cpf != cpf:
        flash('Acesso não autorizado para editar este perfil.', 'danger')
        logout_user()
        return redirect(url_for('login_usuario'))

    usuario_data = encontrar_usuario(cpf) 
    if not usuario_data:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('dashboard_usuario', cpf=current_user.cpf))
    
    usuario = Usuario.from_db_row(usuario_data)

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        endereco = request.form.get('endereco')
        senha = request.form.get('senha', None) 
        novo_cpf = request.form.get('novo_cpf', None) 

        if editar_usuario(cpf, nome, email, endereco, senha, novo_cpf): 
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard_usuario', cpf=novo_cpf if novo_cpf else cpf)) 
        else:
            flash('Erro ao atualizar o perfil. Tente novamente.', 'danger')
            return redirect(url_for('editar_usuario_perfil', cpf=cpf))

    return render_template('editar_usuario.html', usuario=usuario)


@app.route('/editar_empresa/<cnpj>', methods=['GET', 'POST'])
@login_required 
def editar_empresa_perfil(cnpj):

    if not isinstance(current_user, Empresa) or current_user.cnpj != cnpj:
        flash('Acesso não autorizado para editar este perfil.', 'danger')
        logout_user()
        return redirect(url_for('login_empresa'))

    empresa = encontrar_empresa(cnpj)
    if not empresa:
        flash('Empresa não encontrada', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        senha = request.form['senha'] if 'senha' in request.form and request.form['senha'] else None

        if not nome or not endereco:
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(request.url)

        editar_empresa(cnpj, nome, endereco, senha)
        flash('Perfil atualizado com sucesso', 'success')
        return redirect(url_for('perfil_empresa', cnpj=cnpj)) 

    return render_template('editar_empresa.html', empresa=empresa)


@app.route('/perfil_empresa/<cnpj>') 
@login_required
def perfil_empresa(cnpj): 
    print(f"Entrou na rota perfil_empresa para CNPJ: {cnpj}")
    try:
       
        if not current_user.is_an_empresa():
            print(f"current_user não é uma empresa. Tipo: {type(current_user)}")
            flash('Acesso não autorizado.', 'danger')
            logout_user() 
            return redirect(url_for('login_usuario')) 
        
        print(f"current_user é uma empresa. Nome: {current_user.nome}, CNPJ: {current_user.cnpj}")
      
        return render_template('perfil_empresa.html', company=current_user) 
    except Exception as e:
        print(f"ERRO CRÍTICO ao renderizar perfil_empresa: {e}") 
        flash('Ocorreu um erro ao carregar o perfil da empresa. Tente novamente.', 'danger')
        logout_user() 
        return redirect(url_for('login_empresa'))

@app.route('/dashboard_usuario/<cpf>', methods=['GET'])
@login_required 
def dashboard_usuario(cpf):

    if not isinstance(current_user, Usuario) or current_user.cpf != cpf:
        flash('Acesso não autorizado para este perfil.', 'danger')
        logout_user()
        return redirect(url_for('login_usuario'))

    usuario = current_user 
    pedidos = buscar_pedidos_usuarios(usuario.cpf)
    comunicados = buscar_comunicados_usuario(usuario.cpf)
    comunicados_gerais = buscar_comunicado_geral()
    
    ph_atual, historico_ph, nivel_atual, historico_nivel = buscar_dados_cisterna_usuario(usuario.id)
    
    return render_template('dashboard_usuario.html', 
                            usuario=usuario, 
                            pedidos=pedidos, 
                            comunicados=comunicados, 
                            comunicados_gerais=comunicados_gerais,
                            ph_atual=ph_atual,
                            nivel_atual=nivel_atual,
                            historico_ph=historico_ph,
                            historico_nivel=historico_nivel)


@app.route('/solicitar_pedido', methods=['GET', 'POST'])
@login_required 
def solicitar_pedido():

    if not isinstance(current_user, Usuario):
        flash('Apenas usuários podem solicitar pedidos.', 'danger')
        return redirect(url_for('dashboard_usuario', cpf=current_user.cpf)) 

    try:
        if request.method == 'POST':
            cpf = request.form['cpf']

            if cpf != current_user.cpf:
                flash('Você só pode solicitar pedidos para o seu próprio CPF.', 'danger')
                return redirect(url_for('solicitar_pedido'))

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

            criar_pedido(current_user.cpf, descricao, quantidade, data, cnpj_empresa)

            flash('Pedido solicitado com sucesso!', 'success')
            return redirect(url_for('dashboard_usuario', cpf=current_user.cpf))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT cnpj, nome FROM empresas"
        cursor.execute(query)
        empresas = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('solicitar_pedido.html', empresas=empresas, usuario=current_user)
    except Exception as e:
        flash(f'Ocorreu um erro ao processar o pedido: {str(e)}', 'danger')
        return redirect(url_for('solicitar_pedido'))

@app.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def cancelar_pedido(pedido_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT cpf_usuario FROM pedidos WHERE id = %s"
    cursor.execute(query, (pedido_id,))
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()

    if not pedido or pedido['cpf_usuario'] != current_user.cpf:
        flash('Você não tem permissão para cancelar este pedido.', 'danger')
        return redirect(url_for('dashboard_usuario', cpf=current_user.cpf))

    try:
        excluir_pedido(pedido_id)
        flash('Pedido cancelado com sucesso', 'success')
        return redirect(url_for('dashboard_usuario', cpf=current_user.cpf))
    except Exception as e:
        flash(f'Erro ao cancelar pedido: {str(e)}', 'danger')
        return redirect(url_for('dashboard_usuario', cpf=current_user.cpf))
    
@app.route('/excluir_pedido/<int:pedido_id>/<cnpj>', methods=['POST'])
@login_required
def excluir_pedido_view(pedido_id, cnpj):

    if not isinstance(current_user, Empresa) or current_user.cnpj != cnpj:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT cnpj_empresa FROM pedidos WHERE id = %s"
    cursor.execute(query, (pedido_id,))
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()

    if not pedido or pedido['cnpj_empresa'] != current_user.cnpj:
        flash('Você não tem permissão para excluir este pedido.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    excluir_pedido(pedido_id)
    flash('Pedido excluído com sucesso', 'success')
    return redirect(url_for('perfil_empresa', cnpj=cnpj))

@app.route('/alterar_status/<int:pedido_id>/<cnpj>', methods=['POST'])
@login_required 
def alterar_status(pedido_id, cnpj):

    if not isinstance(current_user, Empresa) or current_user.cnpj != cnpj:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT cnpj_empresa FROM pedidos WHERE id = %s"
    cursor.execute(query, (pedido_id,))
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()

    if not pedido or pedido['cnpj_empresa'] != current_user.cnpj:
        flash('Você não tem permissão para alterar o status deste pedido.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    novo_status = request.form['novo_status']
    alterar_status_pedido(pedido_id, novo_status)
    flash('Status do pedido alterado com sucesso', 'success')
    return redirect(url_for('perfil_empresa', cnpj=cnpj))

@app.route('/enviar_comunicado/<int:pedido_id>', methods=['POST'])
@login_required 
def enviar_comunicado_usuario(pedido_id):
    if not isinstance(current_user, Empresa):
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))
    

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT cnpj_empresa FROM pedidos WHERE id = %s"
    cursor.execute(query, (pedido_id,))
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()

    if not pedido or pedido['cnpj_empresa'] != current_user.cnpj:
        flash('Você não tem permissão para enviar comunicado para este pedido.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    mensagem = request.form.get('mensagem')
    if not mensagem:
        flash('Mensagem não fornecida', 'error')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))
    
    enviar_comunicado_pedido(pedido_id, mensagem)
    flash('Comunicado enviado com sucesso', 'success') 
    
    return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

@app.route('/criar_comunicado', methods=['GET', 'POST'])
@login_required
def criar_comunicado():

    if not isinstance(current_user, Empresa):
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    if request.method == 'POST':
        assunto = request.form['assunto']
        mensagem = request.form['mensagem']
        enviar_comunicado_geral(assunto, mensagem)
        flash('Aviso enviado com sucesso!', 'success')

        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    return render_template('criar_comunicado.html')

@app.route('/excluir_comunicado_geral/<int:comunicado_id>', methods=['POST'])
@login_required # Protege a rota
def excluir_comunicado_geral_view(comunicado_id):

    if not isinstance(current_user, Empresa):
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    excluir_comunicado_geral(comunicado_id)
    flash('Aviso excluído com sucesso', 'success')
    return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))
    
@app.route('/pedido/<int:pedido_id>', methods=['GET'])
@login_required
def visualizar_pedido(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query_pedido = """
        SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome, p.cpf_usuario, p.cnpj_empresa
        FROM pedidos p
        JOIN usuarios u ON p.cpf_usuario = u.cpf
        WHERE p.id = %s
    """
    cursor.execute(query_pedido, (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        cursor.close()
        conn.close()
        flash('Pedido não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))


    tem_permissao = False
    if isinstance(current_user, Usuario) and current_user.cpf == pedido['cpf_usuario']:
        tem_permissao = True
    elif isinstance(current_user, Empresa) and current_user.cnpj == pedido['cnpj_empresa']:
        tem_permissao = True
    
    if not tem_permissao:
        cursor.close()
        conn.close()
        flash('Você não tem permissão para visualizar este pedido.', 'danger')

        if isinstance(current_user, Usuario):
            return redirect(url_for('dashboard_usuario', cpf=current_user.cpf))
        elif isinstance(current_user, Empresa):
            return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))
        else:
            return redirect(url_for('pagina_inicial'))


    query_imagens = """
        SELECT id, caminho, tipo_imagem, tem_rachadura
        FROM imagens_pedido
        WHERE pedido_id = %s
    """
    cursor.execute(query_imagens, (pedido_id,))
    imagens = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('pedido_detalhe.html', pedido=pedido, imagens=imagens, current_user_is_empresa=isinstance(current_user, Empresa))


@app.route('/detalhes_cisterna/<cnpj>')
@login_required 
def detalhes_cisterna(cnpj):

    if not isinstance(current_user, Empresa) or current_user.cnpj != cnpj:
        flash('Acesso não autorizado para esta cisterna.', 'danger')
        logout_user()
        return redirect(url_for('login_empresa'))

    empresa = encontrar_empresa(cnpj)
    if not empresa:
        flash('Empresa não encontrada', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

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
@login_required
def analisar_rachadura(pedido_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT cpf_usuario, cnpj_empresa FROM pedidos WHERE id = %s"
    cursor.execute(query, (pedido_id,))
    pedido_info = cursor.fetchone()
    cursor.close()
    conn.close()

    if not pedido_info:
        flash('Pedido não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    tem_permissao = False
    if isinstance(current_user, Usuario) and current_user.cpf == pedido_info['cpf_usuario']:
        tem_permissao = True
    elif isinstance(current_user, Empresa) and current_user.cnpj == pedido_info['cnpj_empresa']:
        tem_permissao = True

    if not tem_permissao:
        flash('Você não tem permissão para enviar imagens para este pedido.', 'danger')
        return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))

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
            os.remove(filepath)
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
@login_required 
def excluir_imagem_view(imagem_id, pedido_id):
    """Rota para excluir uma imagem"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query_pedido = "SELECT cpf_usuario, cnpj_empresa FROM pedidos WHERE id = %s"
    cursor.execute(query_pedido, (pedido_id,))
    pedido_info = cursor.fetchone()
    cursor.close()
    conn.close()

    if not pedido_info:
        flash('Pedido não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    tem_permissao = False
    if isinstance(current_user, Usuario) and current_user.cpf == pedido_info['cpf_usuario']:
        tem_permissao = True
    elif isinstance(current_user, Empresa) and current_user.cnpj == pedido_info['cnpj_empresa']:
        tem_permissao = True

    if not tem_permissao:
        flash('Você não tem permissão para excluir esta imagem.', 'danger')
        return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))

    try:
        if excluir_imagem(imagem_id):
            flash('Imagem excluída com sucesso', 'success')
        else:
            flash('Erro ao excluir imagem', 'danger')
    except Exception as e:
        flash(f'Erro ao excluir imagem: {str(e)}', 'danger')
        
    return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))

@app.route('/api/pedido/<int:pedido_id>')
@login_required
def api_pedido(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome, p.cpf_usuario, p.cnpj_empresa
        FROM pedidos p
        JOIN usuarios u ON p.cpf_usuario = u.cpf
        WHERE p.id = %s
    """
    cursor.execute(query, (pedido_id,))
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if pedido:
        tem_permissao = False
        if isinstance(current_user, Usuario) and current_user.cpf == pedido['cpf_usuario']:
            tem_permissao = True
        elif isinstance(current_user, Empresa) and current_user.cnpj == pedido['cnpj_empresa']:
            tem_permissao = True
        
        if not tem_permissao:
            return jsonify({"error": "Acesso não autorizado para este pedido"}), 403 # 403 Forbidden
            
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
@login_required 
def informacoes_cisterna(cpf):
    if not isinstance(current_user, Usuario) or current_user.cpf != cpf:
        flash('Acesso não autorizado para estas informações de cisterna.', 'danger')
        logout_user()
        return redirect(url_for('login_usuario'))

    usuario = current_user 
    
    ph_atual, historico_ph, nivel_atual, historico_nivel = buscar_dados_cisterna_usuario(usuario.id)
    notificacoes = buscar_notificacoes(usuario.id) 
    
    return render_template('informacoes_cisterna.html', 
                            usuario=usuario,
                            ph_atual=ph_atual, 
                            historico_ph=historico_ph, 
                            nivel_atual=nivel_atual, 
                            historico_nivel=historico_nivel,
                            notificacoes=notificacoes)

@app.route('/rachaduras/<int:pedido_id>')
@login_required
def rachaduras(pedido_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query_pedido = """
            SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome, p.cnpj_empresa, p.cpf_usuario
            FROM pedidos p
            JOIN usuarios u ON p.cpf_usuario = u.cpf
            WHERE p.id = %s
        """
        cursor.execute(query_pedido, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido:
            cursor.close()
            conn.close()
            flash('Pedido não encontrado.', 'danger')
            return redirect(url_for('pagina_inicial'))

        tem_permissao = False
        if isinstance(current_user, Usuario) and current_user.cpf == pedido['cpf_usuario']:
            tem_permissao = True
        elif isinstance(current_user, Empresa) and current_user.cnpj == pedido['cnpj_empresa']:
            tem_permissao = True
        
        if not tem_permissao:
            cursor.close()
            conn.close()
            flash('Você não tem permissão para visualizar estas informações.', 'danger')
            if isinstance(current_user, Usuario):
                return redirect(url_for('dashboard_usuario', cpf=current_user.cpf))
            elif isinstance(current_user, Empresa):
                return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))
            else:
                return redirect(url_for('pagina_inicial'))

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
        flash(f"Erro ao carregar rachaduras: {str(e)}", 'danger')
        return redirect(url_for('pagina_inicial')) 
    
@app.route('/limpar_notificacao/<int:notificacao_id>', methods=['POST'])
@login_required 
def limpar_notificacao(notificacao_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query_notificacao_proprietario = """
            SELECT n.pedido_id, p.cpf_usuario, p.cnpj_empresa
            FROM notificacoes n
            JOIN pedidos p ON n.pedido_id = p.id
            WHERE n.id = %s
        """
        cursor.execute(query_notificacao_proprietario, (notificacao_id,))
        notificacao_info = cursor.fetchone()

        if not notificacao_info:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Notificação não encontrada"}), 404

        tem_permissao = False
        if isinstance(current_user, Usuario) and current_user.cpf == notificacao_info['cpf_usuario']:
            tem_permissao = True
        elif isinstance(current_user, Empresa) and current_user.cnpj == notificacao_info['cnpj_empresa']:
            tem_permissao = True
        
        if not tem_permissao:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Acesso não autorizado para limpar esta notificação"}), 403

        query = "DELETE FROM notificacoes WHERE id = %s"
        cursor.execute(query, (notificacao_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Erro ao limpar notificação: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', current_year=datetime.now().year), 500

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template('404.html', current_year=datetime.now().year), 404

@app.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        if usuario == 'admin' and senha == 'suasenha':
            session['admin_logged_in'] = True
            flash('Login de administrador realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login_admin'))
    return render_template('admin_dashboard.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login_admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)