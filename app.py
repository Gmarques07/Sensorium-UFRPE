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
from typing import Dict, Any, Optional, Union, List, TypedDict, cast, TypeVar
from mysql.connector.types import RowType, MySQLConvertibleType, RowItemType
from decimal import Decimal
from datetime import date, timedelta
from mysql.connector.cursor import MySQLCursorDict


app = Flask(__name__)
app.secret_key = os.urandom(24) 


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_usuario'  # type: ignore
login_manager.login_message = 'Você precisa estar logado para acessar esta página.'
login_manager.login_message_category = 'warning'

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
        imagem = convert_row_to_dict(cursor.fetchone())
        
        if not imagem:
            cursor.close()
            conn.close()
            return False
            
        query_delete = "DELETE FROM imagens_pedido WHERE id = %s"
        cursor.execute(query_delete, (imagem_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        if imagem and isinstance(imagem, dict) and 'caminho' in imagem:
            caminho_str = str(imagem.get('caminho', ''))
            caminho_completo = os.path.join('static', caminho_str)
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
        cursor = conn.cursor(dictionary=True)
        
        query_pedido = "SELECT cpf_usuario, descricao FROM pedidos WHERE id = %s"
        cursor.execute(query_pedido, (pedido_id,))
        pedido = convert_row_to_dict(cursor.fetchone())
        
        if not pedido:
            cursor.close()
            conn.close()
            return False
            
        assunto = f"ALERTA: Rachaduras detectadas no pedido #{pedido_id}"
        mensagem_completa = f"{mensagem}\n\nPedido: {pedido.get('descricao', '')}\nImagem ID: {imagem_id}"
        
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
        usuario_data = cursor.fetchone()
        if usuario_data:
            return Usuario.from_db_row(usuario_data)
        return None
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

def editar_empresa(cnpj: str, nome: Optional[str] = None, endereco: Optional[str] = None, senha: Optional[str] = None) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        set_values = []
        params = []
        query = "UPDATE empresas SET "

        if nome:
            set_values.append("nome = %s")
            params.append(nome)
        if endereco:
            set_values.append("endereco = %s")
            params.append(endereco)
        if senha:
            set_values.append("senha = %s")
            params.append(generate_password_hash(senha))

        if not set_values:
            return False

        query += ", ".join(set_values)
        query += " WHERE cnpj = %s"
        params.append(cnpj)

        cursor.execute(query, tuple(params))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao editar empresa: {e}")
        return False

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
        pedidos = [convert_row_to_dict(row) for row in cursor.fetchall()]
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

# Definindo tipos personalizados para melhor tipagem
class PedidoDict(TypedDict, total=False):
    id: int
    descricao: str
    quantidade: int
    status: str
    data: Optional[datetime]
    usuario_nome: str
    cpf_usuario: str
    cnpj_empresa: str

class NotificacaoDict(TypedDict, total=False):
    id: int
    pedido_id: int
    mensagem: str
    data_criacao: datetime
    cpf_usuario: str
    cnpj_empresa: str

def buscar_notificacoes(id_entidade):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    notificacoes: List[Dict[str, Any]] = []

    if isinstance(id_entidade, str) and len(id_entidade) == 14:
        query_notificacoes = """
            SELECT n.* FROM notificacoes n
            JOIN pedidos p ON n.pedido_id = p.id
            WHERE p.cnpj_empresa = %s
            ORDER BY n.data_criacao DESC
            LIMIT 10
        """
        cursor.execute(query_notificacoes, (id_entidade,))
        notificacoes = convert_rows_to_dicts(cursor.fetchall())
        
        for notif in notificacoes:
            query_imagens = """
                SELECT caminho, tipo_imagem, tem_rachadura
                FROM imagens_pedido
                WHERE pedido_id = %s
            """
            pedido_id = cast(int, notif.get('pedido_id', 0))
            cursor.execute(query_imagens, (pedido_id,))
            notif['imagens'] = convert_rows_to_dicts(cursor.fetchall())

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
        notificacoes = convert_rows_to_dicts(cursor.fetchall())
        
        for notif in notificacoes:
            query_imagens = """
                SELECT caminho, tipo_imagem, tem_rachadura
                FROM imagens_pedido
                WHERE pedido_id = %s
            """
            pedido_id = cast(int, notif.get('pedido_id', 0))
            cursor.execute(query_imagens, (pedido_id,))
            notif['imagens'] = convert_rows_to_dicts(cursor.fetchall())
    
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

def buscar_dados_cisterna_usuario_v2(cpf_usuario):
    """Busca os dados da cisterna de um usuário específico"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Primeiro busca a cisterna do usuário
        query_cisterna = """
            SELECT id, identificador, nome, tipo_equipamento, status
            FROM cisternas 
            WHERE cpf_usuario = %s AND status = 'ativo'
            LIMIT 1
        """
        cursor.execute(query_cisterna, (cpf_usuario,))
        cisterna = cursor.fetchone()
        
        if not cisterna:
            cursor.close()
            conn.close()
            return None, [], None, []
            
        # Busca pH atual
        query_ph_atual = """
            SELECT ph, data 
            FROM ph_niveis_cisterna 
            WHERE cisterna_id = %s 
            ORDER BY data DESC LIMIT 1
        """
        cursor.execute(query_ph_atual, (cisterna['id'],))
        ph_atual = cursor.fetchone()
        
        # Busca histórico de pH
        query_historico_ph = """
            SELECT ph, data 
            FROM ph_niveis_cisterna 
            WHERE cisterna_id = %s 
            ORDER BY data DESC LIMIT 10
        """
        cursor.execute(query_historico_ph, (cisterna['id'],))
        historico_ph = cursor.fetchall()
        
        # Busca nível atual
        query_nivel_atual = """
            SELECT boia, status, data 
            FROM niveis_agua_cisterna 
            WHERE cisterna_id = %s 
            ORDER BY data DESC LIMIT 1
        """
        cursor.execute(query_nivel_atual, (cisterna['id'],))
        nivel_atual = cursor.fetchone()
        
        # Busca histórico de nível
        query_historico_nivel = """
            SELECT boia, status, data 
            FROM niveis_agua_cisterna 
            WHERE cisterna_id = %s 
            ORDER BY data DESC LIMIT 10
        """
        cursor.execute(query_historico_nivel, (cisterna['id'],))
        historico_nivel = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return ph_atual, historico_ph, nivel_atual, historico_nivel
    except Exception as e:
        print(f"Erro ao buscar dados da cisterna do usuário: {e}")
        return None, [], None, []

@app.route('/')
def pagina_inicial():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e), 500

@app.route('/login_usuario', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        
        try:
            usuario = encontrar_usuario(cpf)
            if usuario and check_password_hash(usuario.senha, senha):
                login_user(usuario)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard_usuario_view'))
            else:
                flash('CPF ou senha incorretos.', 'danger')
        except Exception as e:
            print(f"Erro detalhado no login_usuario: {e}")
            flash('Erro ao realizar login.', 'danger')
        
    return render_template('login_usuario.html')

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

@app.route('/editar_usuario/<cpf>', methods=['POST'])
@login_required
def editar_usuario_perfil(cpf):
    if not isinstance(current_user, Usuario) or current_user.cpf != cpf:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        endereco = request.form.get('endereco')
        senha = request.form.get('senha')

        if editar_usuario(cpf, nome, email, endereco, senha):
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard_usuario_view'))
        else:
            flash('Erro ao atualizar perfil.', 'danger')
            return redirect(url_for('dashboard_usuario_view'))

    except Exception as e:
        flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
        return redirect(url_for('dashboard_usuario_view'))

@app.route('/editar_empresa/<cnpj>', methods=['GET', 'POST'])
@login_required
def editar_empresa_perfil(cnpj: str):
    if not isinstance(current_user, Empresa) or current_user.cnpj != cnpj:
        flash('Acesso não autorizado para editar este perfil.', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

    nome = request.form.get('nome')
    endereco = request.form.get('endereco')
    senha = request.form.get('senha')

    if not nome or not endereco:
        flash('Nome e endereço são obrigatórios!', 'danger')
        return redirect(url_for('perfil_empresa', cnpj=cnpj))

    if editar_empresa(cnpj, nome, endereco, senha):
        # Atualiza os dados do usuário na sessão
        empresa_atualizada = encontrar_empresa(cnpj)
        if empresa_atualizada:
            empresa_dict = cast(Dict[str, Any], empresa_atualizada)
            current_user.nome = empresa_dict.get('nome', current_user.nome)
            current_user.endereco = empresa_dict.get('endereco', current_user.endereco)
        flash('Dados atualizados com sucesso!', 'success')
    else:
        flash('Erro ao atualizar os dados. Tente novamente.', 'danger')

    return redirect(url_for('perfil_empresa', cnpj=cnpj))

@app.route('/perfil_empresa/<cnpj>') 
@login_required
def perfil_empresa(cnpj): 
    try:
        # Verificar se o usuário atual tem permissão para ver este perfil
        if not isinstance(current_user, Empresa) or current_user.cnpj != cnpj:
            flash('Você não tem permissão para acessar este perfil.', 'danger')
            return redirect(url_for('pagina_inicial'))
            
        # Buscar dados da empresa
        company = encontrar_empresa(cnpj)
        if not company:
            flash('Empresa não encontrada.', 'danger')
            return redirect(url_for('pagina_inicial'))
            
        # Buscar dados das cisternas
        dados_cisternas = buscar_dados_cisterna(cnpj)
        
        # Buscar comunicados gerais
        comunicados_gerais = buscar_comunicado_geral()
        
        # Buscar pedidos
        pedidos = buscar_pedidos_por_empresa(cnpj)
        
        # Buscar usuários para o cadastro de cisternas
        usuarios = buscar_todos_usuarios()
        
        # Buscar dispositivos disponíveis
        dispositivos_disponiveis = buscar_dispositivos_disponiveis()
        
        return render_template(
            'perfil_empresa.html',
            company=company,
            dados_cisternas=dados_cisternas,
            comunicados_gerais=comunicados_gerais,
            pedidos=pedidos,
            usuarios=usuarios,
            dispositivos_disponiveis=dispositivos_disponiveis
        )
    except Exception as e:
        flash(f'Erro ao carregar o perfil: {str(e)}', 'danger')
        return redirect(url_for('pagina_inicial'))

@app.route('/dashboard_usuario/<cpf>')
@login_required
def dashboard_usuario_by_cpf(cpf):
    # Verificar se o usuário atual tem permissão para ver este dashboard
    if not current_user.is_authenticated or (not current_user.is_an_empresa() and current_user.cpf != cpf):
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pagina_inicial'))
    
    try:
        # Buscar o usuário pelo CPF
        usuario = encontrar_usuario(cpf)
        if not usuario:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('pagina_inicial'))
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados da cisterna e empresa
        cursor.execute(
            """
            SELECT c.*, e.nome as empresa_nome, e.cnpj as empresa_cnpj, e.email as empresa_email
            FROM cisternas c
            JOIN empresas e ON c.cnpj_empresa = e.cnpj
            WHERE c.cpf_usuario = %s AND c.status = 'ativo'
            LIMIT 1
            """,
            (str(cpf),)
        )
        cisterna = cursor.fetchone()
        
        # Buscar comunicados
        cursor.execute(
            """
            SELECT c.*, e.nome as empresa_nome
            FROM comunicado_pedido c
            JOIN pedidos p ON c.pedido_id = p.id
            JOIN empresas e ON p.cnpj_empresa = e.cnpj
            WHERE p.cpf_usuario = %s
            ORDER BY c.data DESC
            """,
            (str(cpf),)
        )
        comunicados = cursor.fetchall()
        
        # Buscar comunicados gerais
        cursor.execute(
            """
            SELECT *
            FROM comunicados_gerais
            ORDER BY data DESC
            """
        )
        comunicados_gerais: List[Dict[str, Any]] = cursor.fetchall()
        
        # Buscar pedidos
        cursor.execute(
            """
            SELECT p.*, e.nome as empresa_nome
            FROM pedidos p
            JOIN empresas e ON p.cnpj_empresa = e.cnpj
            WHERE p.cpf_usuario = %s
            ORDER BY p.data DESC
            """,
            (str(cpf),)
        )
        pedidos = cursor.fetchall()
        
        # Buscar empresas disponíveis para pedidos
        cursor.execute("SELECT cnpj, nome FROM empresas")
        empresas = cursor.fetchall()
        
        # Buscar dados de pH e nível se houver cisterna
        if cisterna:
            ph_atual, historico_ph, nivel_atual, historico_nivel = buscar_dados_cisterna_usuario_v2(str(cpf))
        else:
            ph_atual = None
            historico_ph = []
            nivel_atual = None
            historico_nivel = []
        
        cursor.close()
        conn.close()
        
        return render_template(
            'dashboard_usuario.html',
            usuario=usuario,
            cisterna=cisterna,
            comunicados=comunicados,
            comunicados_gerais=comunicados_gerais,
            pedidos=pedidos,
            empresas=empresas,
            ph_atual=ph_atual,
            historico_ph=historico_ph,
            nivel_atual=nivel_atual,
            historico_nivel=historico_nivel
        )
        
    except Exception as e:
        print(f"Erro no dashboard do usuário: {e}")
        flash('Erro ao carregar o dashboard.', 'danger')
        return redirect(url_for('pagina_inicial'))

@app.route('/api/pedidos')
@login_required
def api_pedidos():
    if not isinstance(current_user, Usuario):
        return jsonify({"error": "Acesso não autorizado"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.*, u.nome AS usuario_nome
        FROM pedidos p
        JOIN usuarios u ON p.cpf_usuario = u.cpf
        WHERE p.cpf_usuario = %s
        ORDER BY p.data DESC
    """
    cursor.execute(query, (current_user.cpf,))
    pedidos = [convert_row_to_dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # Converte datas para string
    for pedido in pedidos:
        if pedido and 'data' in pedido and isinstance(pedido['data'], (datetime, date)):
            pedido['data'] = pedido['data'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify(pedidos)

@app.route('/solicitar_pedido', methods=['GET', 'POST'])
@login_required 
def solicitar_pedido():
    if not isinstance(current_user, Usuario):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Apenas usuários podem solicitar pedidos."}), 403
        flash('Apenas usuários podem solicitar pedidos.', 'danger')
        return redirect(url_for('dashboard_usuario', cpf=current_user.cpf)) 

    try:
        if request.method == 'POST':
            try:
                cpf_usuario = request.form.get('cpf')
                cnpj_empresa = request.form.get('cnpj_empresa')
                descricao = request.form.get('descricao')
                quantidade = request.form.get('quantidade')
                data = request.form.get('data')
                
                if criar_pedido(cpf_usuario, descricao, quantidade, data, cnpj_empresa):
                    flash('Pedido criado com sucesso!', 'success')
                    return redirect(url_for('dashboard_usuario_by_cpf', cpf=current_user.cpf))
                else:
                    flash('Erro ao criar pedido.', 'danger')
                    return redirect(url_for('dashboard_usuario_by_cpf', cpf=current_user.cpf))
                
            except Exception as e:
                flash(f'Erro ao criar pedido: {str(e)}', 'danger')
                return redirect(url_for('dashboard_usuario_by_cpf', cpf=current_user.cpf))
            
        return redirect(url_for('dashboard_usuario_by_cpf', cpf=current_user.cpf))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": f"Ocorreu um erro ao processar o pedido: {str(e)}"}), 500
        flash(f'Ocorreu um erro ao processar o pedido: {str(e)}', 'danger')
        return redirect(url_for('solicitar_pedido'))

@app.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def cancelar_pedido(pedido_id):
    try:
        if excluir_pedido(pedido_id):
            flash('Pedido cancelado com sucesso!', 'success')
        else:
            flash('Erro ao cancelar pedido.', 'danger')
    except Exception as e:
        flash(f'Erro ao cancelar pedido: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard_usuario_by_cpf', cpf=current_user.cpf))
    
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
    pedido = convert_row_to_dict(cursor.fetchone())
    cursor.close()
    conn.close()

    if not pedido or pedido.get('cnpj_empresa') != current_user.cnpj:
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
    pedido = convert_row_to_dict(cursor.fetchone())
    cursor.close()
    conn.close()

    if not pedido or pedido.get('cnpj_empresa') != current_user.cnpj:
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
    pedido = convert_row_to_dict(cursor.fetchone())
    cursor.close()
    conn.close()

    if not pedido or pedido.get('cnpj_empresa') != current_user.cnpj:
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query_pedido = """
            SELECT p.id, p.descricao, p.quantidade, p.status, p.data, u.nome AS usuario_nome, p.cpf_usuario, p.cnpj_empresa
            FROM pedidos p
            JOIN usuarios u ON p.cpf_usuario = u.cpf
            WHERE p.id = %s
        """
        cursor.execute(query_pedido, (pedido_id,))
        pedido = convert_row_to_dict(cursor.fetchone())

        if not pedido:
            cursor.close()
            conn.close()
            flash('Pedido não encontrado.', 'danger')
            return redirect(url_for('pagina_inicial'))

        tem_permissao = False
        if isinstance(current_user, Usuario) and current_user.cpf == pedido.get('cpf_usuario'):
            tem_permissao = True
        elif isinstance(current_user, Empresa) and current_user.cnpj == pedido.get('cnpj_empresa'):
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
    except Exception as e:
        flash(f'Erro ao visualizar pedido: {str(e)}', 'danger')
        return redirect(url_for('dashboard_usuario_by_cpf', cpf=current_user.cpf))

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
    pedido_info = convert_row_to_dict(cursor.fetchone())
    cursor.close()
    conn.close()

    if not pedido_info:
        flash('Pedido não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    tem_permissao = False
    if isinstance(current_user, Usuario) and current_user.cpf == pedido_info.get('cpf_usuario'):
        tem_permissao = True
    elif isinstance(current_user, Empresa) and current_user.cnpj == pedido_info.get('cnpj_empresa'):
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
        if file.filename:
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
        else:
            flash('Nome do arquivo inválido', 'danger')
            return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))
    except Exception as e:
        print(f"Erro ao analisar rachadura: {e}")
        flash(f"Erro ao processar a imagem: {str(e)}", 'danger')
        return redirect(url_for('visualizar_pedido', pedido_id=pedido_id))
 
@app.route('/excluir_imagem/<int:imagem_id>/<int:pedido_id>', methods=['POST'])
@login_required 
def excluir_imagem_view(imagem_id, pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query_pedido = "SELECT cpf_usuario, cnpj_empresa FROM pedidos WHERE id = %s"
    cursor.execute(query_pedido, (pedido_id,))
    pedido_info = convert_row_to_dict(cursor.fetchone())
    cursor.close()
    conn.close()

    if not pedido_info:
        flash('Pedido não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    tem_permissao = False
    if isinstance(current_user, Usuario) and current_user.cpf == pedido_info.get('cpf_usuario'):
        tem_permissao = True
    elif isinstance(current_user, Empresa) and current_user.cnpj == pedido_info.get('cnpj_empresa'):
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
    pedido = convert_row_to_dict(cursor.fetchone())
    cursor.close()
    conn.close()
    
    if pedido:
        tem_permissao = False
        if isinstance(current_user, Usuario) and current_user.cpf == pedido.get('cpf_usuario'):
            tem_permissao = True
        elif isinstance(current_user, Empresa) and current_user.cnpj == pedido.get('cnpj_empresa'):
            tem_permissao = True
        
        if not tem_permissao:
            return jsonify({"error": "Acesso não autorizado para este pedido"}), 403 
            
        data = pedido.get('data')
        if isinstance(data, (datetime, date)):
            pedido['data'] = data.strftime('%Y-%m-%d %H:%M:%S')
        else:
            pedido['data'] = None
            
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
    try:
        # Lógica existente...
        return render_template('informacoes_cisterna.html', cisterna=cisterna)
    except Exception as e:
        flash(f'Erro ao carregar informações da cisterna: {str(e)}', 'danger')
        return redirect(url_for('dashboard_usuario_by_cpf', cpf=cpf))

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
        pedido = convert_row_to_dict(cursor.fetchone())
        
        if not pedido:
            cursor.close()
            conn.close()
            flash('Pedido não encontrado.', 'danger')
            return redirect(url_for('pagina_inicial'))

        tem_permissao = False
        if isinstance(current_user, Usuario) and current_user.cpf == pedido.get('cpf_usuario'):
            tem_permissao = True
        elif isinstance(current_user, Empresa) and current_user.cnpj == pedido.get('cnpj_empresa'):
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
        cursor.execute(query_empresa, (pedido.get('cnpj_empresa'),))
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
        # Lógica existente...
        return redirect(url_for('dashboard_usuario_by_cpf', cpf=current_user.cpf))
    except Exception as e:
        flash(f'Erro ao limpar notificação: {str(e)}', 'danger')
        return redirect(url_for('dashboard_usuario_by_cpf', cpf=current_user.cpf))

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

def criar_tabelas_admin():
    """Cria as tabelas necessárias para o admin se não existirem"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Criar tabela de notificações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notificacoes_admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tipo VARCHAR(50) NOT NULL,
                titulo VARCHAR(255) NOT NULL,
                mensagem TEXT NOT NULL,
                lida BOOLEAN DEFAULT FALSE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_leitura TIMESTAMP NULL
            )
        """)
        
        # Criar tabela de configurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes_sistema (
                id INT AUTO_INCREMENT PRIMARY KEY,
                chave VARCHAR(100) NOT NULL UNIQUE,
                valor TEXT NOT NULL,
                descricao VARCHAR(255),
                tipo VARCHAR(50) NOT NULL,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Inserir configurações padrão se não existirem
        cursor.execute("""
            INSERT IGNORE INTO configuracoes_sistema (chave, valor, descricao, tipo) VALUES 
            ('limite_pedidos', '1000', 'Quantidade mínima de litros por pedido', 'numero'),
            ('tempo_analise', '24', 'Tempo máximo para análise de pedidos (horas)', 'numero'),
            ('notificacoes_ativas', 'true', 'Ativar sistema de notificações', 'booleano'),
            ('mensagem_manutencao', '', 'Mensagem exibida durante manutenção', 'texto'),
            ('horarios_entrega', '{"inicio": "08:00", "fim": "18:00"}', 'Horários permitidos para entrega', 'json')
        """)
        
        conn.commit()
        
        # Criar notificações de exemplo
        criar_notificacoes_exemplo()
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao criar tabelas admin: {e}")
        return False

def criar_notificacoes_exemplo():
    """Cria algumas notificações de exemplo para o admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Limpar notificações existentes
        cursor.execute("DELETE FROM notificacoes_admin")
        
        # Inserir notificações de exemplo
        notificacoes = [
            ('usuario', 'Novo usuário cadastrado', 'Um novo usuário se cadastrou no sistema.'),
            ('empresa', 'Nova empresa registrada', 'Uma nova empresa foi registrada e precisa de aprovação.'),
            ('pedido', 'Pedido urgente', 'Novo pedido marcado como urgente necessita de atenção.'),
            ('sistema', 'Backup realizado', 'Backup automático do sistema foi concluído com sucesso.'),
            ('sistema', 'Atualização disponível', 'Uma nova atualização do sistema está disponível.')
        ]
        
        query = """
            INSERT INTO notificacoes_admin (tipo, titulo, mensagem) 
            VALUES (%s, %s, %s)
        """
        cursor.executemany(query, notificacoes)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao criar notificações de exemplo: {e}")
        return False

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login_admin'))
    try:
        # Garantir que as tabelas existam
        criar_tabelas_admin()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar dados existentes
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        total_usuarios = len(usuarios)

        cursor.execute("SELECT * FROM empresas")
        empresas = cursor.fetchall()
        total_empresas = len(empresas)

        cursor.execute("""
            SELECT p.*, u.nome AS usuario_nome, e.nome AS empresa_nome
            FROM pedidos p
            LEFT JOIN usuarios u ON p.cpf_usuario = u.cpf
            LEFT JOIN empresas e ON p.cnpj_empresa = e.cnpj
            ORDER BY p.data DESC
        """)
        pedidos = cursor.fetchall()
        total_pedidos = len(pedidos)

        # Buscar notificações não lidas
        cursor.execute("""
            SELECT * FROM notificacoes_admin 
            WHERE lida = FALSE 
            ORDER BY data_criacao DESC
        """)
        notificacoes = cursor.fetchall()

        # Buscar configurações
        cursor.execute("SELECT * FROM configuracoes_sistema ORDER BY chave")
        configuracoes = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            'admin_dashboard.html',
            total_usuarios=total_usuarios,
            usuarios=usuarios,
            total_empresas=total_empresas,
            empresas=empresas,
            total_pedidos=total_pedidos,
            pedidos=pedidos,
            notificacoes=notificacoes,
            configuracoes=configuracoes
        )
    except Exception as e:
        print(f"Erro ao carregar dashboard admin: {e}")
        return render_template('admin_dashboard.html', 
                             total_usuarios=0, usuarios=[], 
                             total_empresas=0, empresas=[], 
                             total_pedidos=0, pedidos=[],
                             notificacoes=[], configuracoes=[])

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login_admin'))

T = TypeVar('T', bound=Union[Dict[str, Any], None])

def convert_row_to_dict(row: Any) -> Optional[Dict[str, Any]]:
    """Converte uma linha do cursor MySQL para um dicionário.
    
    Args:
        row: Uma linha retornada pelo cursor MySQL
        
    Returns:
        Um dicionário com os dados da linha ou None se a linha for None
    """
    if row is None:
        return None
    try:
        # Se já é um dicionário, retorna uma cópia
        if isinstance(row, dict):
            return dict(row)
        # Se é uma sequência, converte para dicionário usando índices como chaves
        if isinstance(row, (list, tuple)):
            return {str(i): v for i, v in enumerate(row)}
        # Tenta converter para dicionário
        return dict(row)
    except (TypeError, ValueError, AttributeError):
        return None

def convert_rows_to_dicts(rows: Any) -> List[Dict[str, Any]]:
    """Converte uma lista de linhas do cursor MySQL para uma lista de dicionários.
    
    Args:
        rows: Uma lista de linhas retornadas pelo cursor MySQL
        
    Returns:
        Uma lista de dicionários com os dados das linhas
    """
    if rows is None:
        return []
    result = []
    for row in rows:
        converted = convert_row_to_dict(row)
        if converted is not None:
            result.append(converted)
    return result

# --- ROTAS ADMIN PARA USO VIA AJAX (JSON) ---

# Usuários
@app.route('/admin/usuario/<int:id>', methods=['GET'])
def admin_ver_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    if usuario:
        return jsonify({'success': True, 'usuario': usuario})
    return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 404

@app.route('/admin/usuario/<int:id>', methods=['POST'])
def admin_editar_usuario(id):
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE usuarios SET nome=%s, cpf=%s, email=%s, endereco=%s WHERE id=%s"
    cursor.execute(query, (data.get('nome'), data.get('cpf'), data.get('email'), data.get('endereco'), id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/usuario/<int:id>', methods=['DELETE'])
def admin_excluir_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# Empresas
@app.route('/admin/empresa/<int:id>', methods=['GET'])
def admin_ver_empresa(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM empresas WHERE id = %s", (id,))
    empresa = cursor.fetchone()
    cursor.close()
    conn.close()
    if empresa:
        return jsonify({'success': True, 'empresa': empresa})
    return jsonify({'success': False, 'error': 'Empresa não encontrada'}), 404

@app.route('/admin/empresa/<int:id>', methods=['POST'])
def admin_editar_empresa(id):
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE empresas SET nome=%s, cnpj=%s, email=%s, endereco=%s WHERE id=%s"
    cursor.execute(query, (data.get('nome'), data.get('cnpj'), data.get('email'), data.get('endereco'), id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/empresa/<int:id>', methods=['DELETE'])
def admin_excluir_empresa(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM empresas WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# Pedidos
@app.route('/admin/pedido/<int:id>', methods=['GET'])
def admin_ver_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT p.*, u.nome AS usuario_nome, e.nome AS empresa_nome FROM pedidos p LEFT JOIN usuarios u ON p.cpf_usuario = u.cpf LEFT JOIN empresas e ON p.cnpj_empresa = e.cnpj WHERE p.id = %s", (id,))
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()
    if pedido:
        return jsonify({'success': True, 'pedido': pedido})
    return jsonify({'success': False, 'error': 'Pedido não encontrado'}), 404

@app.route('/admin/pedido/<int:id>', methods=['POST'])
def admin_editar_pedido(id):
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE pedidos SET descricao=%s, quantidade=%s, status=%s, data=%s, cpf_usuario=%s, cnpj_empresa=%s WHERE id=%s"
    cursor.execute(query, (
        data.get('descricao'),
        data.get('quantidade'),
        data.get('status'),
        data.get('data'),
        data.get('cpf_usuario'),
        data.get('cnpj_empresa'),
        id
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/pedido/<int:id>', methods=['DELETE'])
def admin_excluir_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pedidos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

def criar_notificacao_admin(tipo, titulo, mensagem):
    """Cria uma nova notificação para o admin"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO notificacoes_admin (tipo, titulo, mensagem) VALUES (%s, %s, %s)"
    cursor.execute(query, (tipo, titulo, mensagem))
    conn.commit()
    cursor.close()
    conn.close()

def buscar_notificacoes_admin(apenas_nao_lidas=False):
    """Busca notificações do admin"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if apenas_nao_lidas:
        query = "SELECT * FROM notificacoes_admin WHERE lida = FALSE ORDER BY data_criacao DESC"
    else:
        query = "SELECT * FROM notificacoes_admin ORDER BY data_criacao DESC"
    
    cursor.execute(query)
    notificacoes = cursor.fetchall()
    cursor.close()
    conn.close()
    return notificacoes

def marcar_notificacao_como_lida(notificacao_id):
    """Marca uma notificação como lida"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE notificacoes_admin SET lida = TRUE, data_leitura = CURRENT_TIMESTAMP WHERE id = %s"
    cursor.execute(query, (notificacao_id,))
    conn.commit()
    cursor.close()
    conn.close()

def buscar_configuracoes():
    """Busca todas as configurações do sistema"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM configuracoes_sistema ORDER BY chave"
    cursor.execute(query)
    configuracoes = cursor.fetchall()
    cursor.close()
    conn.close()
    return configuracoes

def atualizar_configuracao(chave, valor):
    """Atualiza o valor de uma configuração"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE configuracoes_sistema SET valor = %s WHERE chave = %s"
    cursor.execute(query, (valor, chave))
    conn.commit()
    cursor.close()
    conn.close()

# Rotas para notificações
@app.route('/admin/notificacoes')
def admin_notificacoes():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    notificacoes = buscar_notificacoes_admin()
    return jsonify({'success': True, 'notificacoes': notificacoes})

@app.route('/admin/notificacoes/nao-lidas')
def admin_notificacoes_nao_lidas():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    try:
        # Garantir que as tabelas existam
        criar_tabelas_admin()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM notificacoes_admin 
            WHERE lida = FALSE 
            ORDER BY data_criacao DESC
        """)
        notificacoes = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'notificacoes': notificacoes})
    except Exception as e:
        print(f"Erro ao buscar notificações: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/notificacoes/<int:notificacao_id>/marcar-lida', methods=['POST'])
def admin_marcar_notificacao_lida(notificacao_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    marcar_notificacao_como_lida(notificacao_id)
    return jsonify({'success': True})

# Rotas para configurações
@app.route('/admin/configuracoes')
def admin_configuracoes():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    configuracoes = buscar_configuracoes()
    return jsonify({'success': True, 'configuracoes': configuracoes})

@app.route('/admin/configuracoes/<chave>', methods=['POST'])
def admin_atualizar_configuracao(chave):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    data = request.get_json()
    if not data or 'valor' not in data:
        return jsonify({'success': False, 'error': 'Valor não fornecido'}), 400
        
    atualizar_configuracao(chave, data['valor'])
    return jsonify({'success': True})

def cadastrar_cisterna(identificador, nome, tipo_equipamento, cpf_usuario, cnpj_empresa, dispositivo_id=None):
    """
    Cadastra uma nova cisterna no sistema.
    Se dispositivo_id for fornecido, vincula a cisterna ao dispositivo.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar se o usuário já tem uma cisterna ativa
        cursor.execute(
            "SELECT id FROM cisternas WHERE cpf_usuario = %s AND status = 'ativo'",
            (cpf_usuario,)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "Usuário já possui uma cisterna ativa"

        # Se um dispositivo foi fornecido, verificar se está disponível
        if dispositivo_id:
            cursor.execute(
                "SELECT id, status FROM dispositivos WHERE id = %s",
                (dispositivo_id,)
            )
            dispositivo = cursor.fetchone()
            if not dispositivo:
                cursor.close()
                conn.close()
                return False, "Dispositivo não encontrado"
            if dispositivo['status'] != 'disponivel':
                cursor.close()
                conn.close()
                return False, "Dispositivo não está disponível"

        # Inserir a nova cisterna
        cursor.execute(
            """
            INSERT INTO cisternas 
            (nome, tipo_equipamento, data_instalacao, status, cpf_usuario, cnpj_empresa, dispositivo_id)
            VALUES (%s, %s, NOW(), 'ativo', %s, %s, %s)
            """,
            (nome, tipo_equipamento, cpf_usuario, cnpj_empresa, dispositivo_id)
        )

        # Se um dispositivo foi fornecido, atualizá-lo para em_uso
        if dispositivo_id:
            cursor.execute(
                "UPDATE dispositivos SET status = 'em_uso' WHERE id = %s",
                (dispositivo_id,)
            )

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Cisterna cadastrada com sucesso"

    except Exception as e:
        print(f"Erro ao cadastrar cisterna: {e}")
        return False, str(e)

def buscar_cisterna_usuario(cpf_usuario):
    """Busca a cisterna associada a um usuário específico"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT c.*, e.nome as empresa_nome
            FROM cisternas c
            JOIN empresas e ON c.cnpj_empresa = e.cnpj
            WHERE c.cpf_usuario = %s AND c.status = 'ativo'
        """
        cursor.execute(query, (cpf_usuario,))
        cisterna = cursor.fetchone()
        cursor.close()
        conn.close()
        return cisterna
    except Exception as e:
        print(f"Erro ao buscar cisterna do usuário: {e}")
        return None

def buscar_cisternas_empresa(cnpj_empresa):
    """Busca todas as cisternas associadas a uma empresa"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT c.*, u.nome as usuario_nome
            FROM cisternas c
            JOIN usuarios u ON c.cpf_usuario = u.cpf
            WHERE c.cnpj_empresa = %s
        """
        cursor.execute(query, (cnpj_empresa,))
        cisternas = cursor.fetchall()
        cursor.close()
        conn.close()
        return cisternas
    except Exception as e:
        print(f"Erro ao buscar cisternas da empresa: {e}")
        return []

def registrar_leitura_ph(cisterna_id, ph):
    """Registra uma nova leitura de pH para uma cisterna específica"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO ph_niveis_cisterna (cisterna_id, ph) VALUES (%s, %s)"
        cursor.execute(query, (cisterna_id, ph))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao registrar leitura de pH: {e}")
        return False

def registrar_nivel_agua(cisterna_id, boia, status):
    """Registra um novo nível de água para uma cisterna específica"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO niveis_agua_cisterna (cisterna_id, boia, status) VALUES (%s, %s, %s)"
        cursor.execute(query, (cisterna_id, boia, status))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao registrar nível de água: {e}")
        return False

def buscar_dados_cisterna_usuario(cpf_usuario):
    """Busca os dados da cisterna de um usuário específico"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Primeiro busca a cisterna do usuário
        query_cisterna = """
            SELECT id, identificador, nome, tipo_equipamento, status
            FROM cisternas 
            WHERE cpf_usuario = %s AND status = 'ativo'
            LIMIT 1
        """
        cursor.execute(query_cisterna, (cpf_usuario,))
        cisterna = cursor.fetchone()
        
        if not cisterna:
            cursor.close()
            conn.close()
            return None, [], None, []
            
        # Busca pH atual
        query_ph_atual = """
            SELECT ph, data 
            FROM ph_niveis_cisterna 
            WHERE cisterna_id = %s 
            ORDER BY data DESC LIMIT 1
        """
        cursor.execute(query_ph_atual, (cisterna['id'],))
        ph_atual = cursor.fetchone()
        
        # Busca histórico de pH
        query_historico_ph = """
            SELECT ph, data 
            FROM ph_niveis_cisterna 
            WHERE cisterna_id = %s 
            ORDER BY data DESC LIMIT 10
        """
        cursor.execute(query_historico_ph, (cisterna['id'],))
        historico_ph = cursor.fetchall()
        
        # Busca nível atual
        query_nivel_atual = """
            SELECT boia, status, data 
            FROM niveis_agua_cisterna 
            WHERE cisterna_id = %s 
            ORDER BY data DESC LIMIT 1
        """
        cursor.execute(query_nivel_atual, (cisterna['id'],))
        nivel_atual = cursor.fetchone()
        
        # Busca histórico de nível
        query_historico_nivel = """
            SELECT boia, status, data 
            FROM niveis_agua_cisterna 
            WHERE cisterna_id = %s 
            ORDER BY data DESC LIMIT 10
        """
        cursor.execute(query_historico_nivel, (cisterna['id'],))
        historico_nivel = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return ph_atual, historico_ph, nivel_atual, historico_nivel
    except Exception as e:
        print(f"Erro ao buscar dados da cisterna do usuário: {e}")
        return None, [], None, []

def buscar_dados_cisterna_empresa(cnpj_empresa):
    """Busca os dados de todas as cisternas de uma empresa"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Busca todas as cisternas da empresa com informações do usuário
        query_cisternas = """
            SELECT c.*, u.nome as usuario_nome
            FROM cisternas c
            JOIN usuarios u ON c.cpf_usuario = u.cpf
            WHERE c.cnpj_empresa = %s
        """
        cursor.execute(query_cisternas, (cnpj_empresa,))
        cisternas = cursor.fetchall()
        
        dados_cisternas = []
        
        for cisterna in cisternas:
            # Busca pH atual
            query_ph_atual = """
                SELECT ph, data 
                FROM ph_niveis_cisterna 
                WHERE cisterna_id = %s 
                ORDER BY data DESC LIMIT 1
            """
            cursor.execute(query_ph_atual, (cisterna['id'],))
            ph_atual = cursor.fetchone()
            
            # Busca nível atual
            query_nivel_atual = """
                SELECT boia, status, data 
                FROM niveis_agua_cisterna 
                WHERE cisterna_id = %s 
                ORDER BY data DESC LIMIT 1
            """
            cursor.execute(query_nivel_atual, (cisterna['id'],))
            nivel_atual = cursor.fetchone()
            
            dados_cisternas.append({
                'cisterna': cisterna,
                'ph_atual': ph_atual,
                'nivel_atual': nivel_atual
            })
        
        cursor.close()
        conn.close()
        
        return dados_cisternas
    except Exception as e:
        print(f"Erro ao buscar dados das cisternas da empresa: {e}")
        return []

def buscar_dispositivos_disponiveis() -> List[Dict[str, Any]]:
    """Busca todos os dispositivos disponíveis para vinculação"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, tipo_equipamento, data_registro 
            FROM dispositivos 
            WHERE status = 'disponivel'
            ORDER BY data_registro DESC
            """
        )
        dispositivos = cursor.fetchall()
        cursor.close()
        conn.close()
        return dispositivos
    except Exception as e:
        print(f"Erro ao buscar dispositivos: {e}")
        return []

@app.route('/cadastrar_cisterna', methods=['GET', 'POST'])
@login_required
def cadastrar_cisterna_route():
    """Rota para cadastrar uma nova cisterna"""
    if not isinstance(current_user, Empresa):
        flash('Apenas empresas podem cadastrar cisternas.', 'danger')
        return redirect(url_for('pagina_inicial'))
        
    if request.method == 'POST':
        nome = request.form.get('nome')
        tipo_equipamento = request.form.get('tipo_equipamento')
        cpf_usuario = request.form.get('cpf_usuario')
        status = request.form.get('status')
        dispositivo_id = request.form.get('dispositivo_id')  # Campo opcional
        
        if not all([nome, tipo_equipamento, cpf_usuario, status]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))
            
        sucesso, mensagem = cadastrar_cisterna(
            identificador=None,  # Não usado mais
            nome=nome,
            tipo_equipamento=tipo_equipamento,
            cpf_usuario=cpf_usuario,
            cnpj_empresa=current_user.cnpj,
            dispositivo_id=dispositivo_id if dispositivo_id else None
        )
        
        if sucesso:
            flash('Cisterna cadastrada com sucesso!', 'success')
        else:
            flash(f'Erro ao cadastrar cisterna: {mensagem}', 'danger')
            
        return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))
        
    # Se for GET, redireciona para o perfil da empresa onde está o modal
    return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

@app.route('/api/sensor/dados', methods=['POST'])
def receber_dados_sensor():
    """
    Recebe dados dos sensores (Arduino/Raspberry) e salva no banco de dados.
    Espera um JSON no formato:
    {
        "dispositivo_id": "string", # MAC address para Arduino ou UUID para Raspberry Pi
        "tipo": "ph" ou "nivel",
        "valor": float,
        "status": string (opcional, apenas para nível)
    }
    """
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ('dispositivo_id', 'tipo', 'valor')):
            return jsonify({'error': 'Dados incompletos'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Atualizar última comunicação do dispositivo
        cursor.execute(
            "UPDATE dispositivos SET ultima_comunicacao = NOW() WHERE id = %s",
            (dados['dispositivo_id'],)
        )
        
        # Buscar a cisterna vinculada ao dispositivo
        cursor.execute(
            "SELECT id FROM cisternas WHERE dispositivo_id = %s",
            (dados['dispositivo_id'],)
        )
        cisterna = cursor.fetchone()
        
        if not cisterna:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Dispositivo não vinculado a nenhuma cisterna'}), 404
            
        # Registrar leitura conforme o tipo
        if dados['tipo'] == 'ph':
            registrar_leitura_ph(cisterna['id'], float(dados['valor']))
        elif dados['tipo'] == 'nivel':
            status = dados.get('status', 'BAIXO' if float(dados['valor']) == 0 else 'ALTO')
            registrar_nivel_agua(cisterna['id'], int(dados['valor']), status)
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Tipo de leitura inválido'}), 400
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Dados registrados com sucesso'}), 201
        
    except Exception as e:
        print(f"Erro ao receber dados do sensor: {e}")
        return jsonify({'error': str(e)}), 500

def buscar_todos_usuarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, cpf, nome FROM usuarios ORDER BY nome"
        cursor.execute(query)
        usuarios = [convert_row_to_dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return usuarios
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return []

@app.route('/excluir_cisterna/<int:cisterna_id>', methods=['POST'])
@login_required
def excluir_cisterna(cisterna_id):
    if not isinstance(current_user, Empresa):
        flash('Apenas empresas podem excluir cisternas.', 'danger')
        return redirect(url_for('pagina_inicial'))
        
    try:
        # Primeiro verifica se a cisterna pertence à empresa logada
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM cisternas WHERE id = %s AND cnpj_empresa = %s"
        cursor.execute(query, (cisterna_id, current_user.cnpj))
        cisterna = cursor.fetchone()
        
        if not cisterna:
            flash('Cisterna não encontrada ou não pertence a esta empresa.', 'danger')
            return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))
        
        # Exclui a cisterna
        query = "DELETE FROM cisternas WHERE id = %s"
        cursor.execute(query, (cisterna_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        flash('Cisterna excluída com sucesso!', 'success')
        
    except Exception as e:
        print(f"Erro ao excluir cisterna: {e}")
        flash('Erro ao excluir cisterna.', 'danger')
        
    return redirect(url_for('perfil_empresa', cnpj=current_user.cnpj))

@app.route('/api/usuario/<cpf>/cisterna/<int:cisterna_id>/relatorio')
@login_required
def gerar_relatorio_usuario(cpf: str, cisterna_id: int):
    """Gera um relatório detalhado do usuário e sua cisterna"""
    try:
        if not isinstance(current_user, Empresa):
            return jsonify({'error': 'Acesso não autorizado'}), 403
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar informações do usuário
        cursor.execute(
            "SELECT nome, cpf, email, endereco FROM usuarios WHERE cpf = %s",
            (str(cpf),)
        )
        usuario: Optional[Dict[str, Any]] = cursor.fetchone()
        
        if not usuario:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        # Buscar informações da cisterna
        cursor.execute(
            """
            SELECT identificador, nome, tipo_equipamento, data_instalacao, status
            FROM cisternas 
            WHERE id = %s AND cpf_usuario = %s
            """,
            (int(cisterna_id), str(cpf))
        )
        cisterna: Optional[Dict[str, Any]] = cursor.fetchone()
        
        if not cisterna:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cisterna não encontrada'}), 404
            
        # Calcular estatísticas
        # Média de pH dos últimos 30 dias
        cursor.execute(
            """
            SELECT COALESCE(AVG(ph), 0) as media_ph
            FROM ph_niveis_cisterna
            WHERE cisterna_id = %s
            AND data >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """,
            (int(cisterna_id),)
        )
        media_ph: float = float(cursor.fetchone()['media_ph'])
        
        # Contagem de alertas de nível baixo nos últimos 30 dias
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM niveis_agua_cisterna
            WHERE cisterna_id = %s
            AND status = 'BAIXO'
            AND data >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """,
            (int(cisterna_id),)
        )
        alertas_nivel: int = int(cursor.fetchone()['total'])
        
        # Contagem de manutenções
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM notificacoes
            WHERE cisterna_id = %s
            AND tipo = 'manutencao'
            AND data_criacao >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """,
            (int(cisterna_id),)
        )
        manutencoes: int = int(cursor.fetchone()['total'])
        
        # Buscar últimas atividades
        cursor.execute(
            """
            (SELECT 
                data as data_atividade,
                'pH' as tipo,
                CONCAT('Leitura de pH: ', CAST(ph AS CHAR)) as descricao
            FROM ph_niveis_cisterna
            WHERE cisterna_id = %s
            ORDER BY data DESC
            LIMIT 5)
            UNION ALL
            (SELECT 
                data as data_atividade,
                'Nível' as tipo,
                CONCAT('Nível de água: ', status) as descricao
            FROM niveis_agua_cisterna
            WHERE cisterna_id = %s
            ORDER BY data DESC
            LIMIT 5)
            UNION ALL
            (SELECT 
                data_criacao as data_atividade,
                'Manutenção' as tipo,
                mensagem as descricao
            FROM notificacoes
            WHERE cisterna_id = %s
            ORDER BY data_criacao DESC
            LIMIT 5)
            ORDER BY data_atividade DESC
            LIMIT 10
            """,
            (int(cisterna_id), int(cisterna_id), int(cisterna_id))
        )
        atividades: List[Dict[str, Any]] = cursor.fetchall()
        
        # Formatar datas para o relatório
        cisterna['data_instalacao'] = cisterna['data_instalacao'].strftime('%d/%m/%Y %H:%M')
        for atividade in atividades:
            atividade['data'] = atividade.pop('data_atividade').strftime('%d/%m/%Y %H:%M')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'usuario': usuario,
            'cisterna': cisterna,
            'estatisticas': {
                'media_ph': round(media_ph, 2),
                'alertas_nivel': alertas_nivel,
                'manutencoes': manutencoes
            },
            'atividades': atividades
        })
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return jsonify({'error': 'Erro ao gerar relatório'}), 500

@app.route('/dashboard_usuario')
@login_required
def dashboard_usuario_view():
    if not isinstance(current_user, Usuario):
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pagina_inicial'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados da cisterna e empresa
        cursor.execute(
            """
            SELECT c.*, e.nome as empresa_nome, e.cnpj as empresa_cnpj, e.email as empresa_email
            FROM cisternas c
            JOIN empresas e ON c.cnpj_empresa = e.cnpj
            WHERE c.cpf_usuario = %s AND c.status = 'ativo'
            LIMIT 1
            """,
            (str(current_user.cpf),)
        )
        cisterna: Optional[Dict[str, Any]] = cursor.fetchone()
        
        # Buscar comunicados
        cursor.execute(
            """
            SELECT c.*, e.nome as empresa_nome
            FROM comunicado_pedido c
            JOIN pedidos p ON c.pedido_id = p.id
            JOIN empresas e ON p.cnpj_empresa = e.cnpj
            WHERE p.cpf_usuario = %s
            ORDER BY c.data DESC
            """,
            (str(current_user.cpf),)
        )
        comunicados: List[Dict[str, Any]] = cursor.fetchall()
        
        # Buscar comunicados gerais
        cursor.execute(
            """
            SELECT *
            FROM comunicados_gerais
            ORDER BY data DESC
            """
        )
        comunicados_gerais: List[Dict[str, Any]] = cursor.fetchall()
        
        # Buscar pedidos
        cursor.execute(
            """
            SELECT p.*, e.nome as empresa_nome
            FROM pedidos p
            JOIN empresas e ON p.cnpj_empresa = e.cnpj
            WHERE p.cpf_usuario = %s
            ORDER BY p.data DESC
            """,
            (str(current_user.cpf),)
        )
        pedidos: List[Dict[str, Any]] = cursor.fetchall()
        
        # Buscar empresas disponíveis para pedidos
        cursor.execute("SELECT cnpj, nome FROM empresas")
        empresas: List[Dict[str, Any]] = cursor.fetchall()
        
        # Buscar dados de pH e nível se houver cisterna
        if cisterna:
            ph_atual, historico_ph, nivel_atual, historico_nivel = buscar_dados_cisterna_usuario_v2(current_user.cpf)
        else:
            ph_atual = None
            historico_ph = []
            nivel_atual = None
            historico_nivel = []
        
        cursor.close()
        conn.close()
        
        return render_template(
            'dashboard_usuario.html',
            usuario=current_user,
            cisterna=cisterna,
            comunicados=comunicados,
            comunicados_gerais=comunicados_gerais,
            pedidos=pedidos,
            empresas=empresas,
            ph_atual=ph_atual,
            historico_ph=historico_ph,
            nivel_atual=nivel_atual,
            historico_nivel=historico_nivel
        )
        
    except Exception as e:
        print(f"Erro no dashboard do usuário: {e}")
        flash('Erro ao carregar o dashboard.', 'danger')
        return redirect(url_for('pagina_inicial'))

def registrar_dispositivo(dispositivo_id: str, tipo_equipamento: str) -> bool:
    """Registra um novo dispositivo IoT no sistema."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se o dispositivo já existe
        cursor.execute("SELECT id FROM dispositivos WHERE id = %s", (dispositivo_id,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False
            
        # Registrar novo dispositivo
        cursor.execute(
            "INSERT INTO dispositivos (id, tipo_equipamento) VALUES (%s, %s)",
            (dispositivo_id, tipo_equipamento)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao registrar dispositivo: {e}")
        return False

def buscar_dispositivos_disponiveis() -> List[Dict[str, Any]]:
    """Retorna lista de dispositivos disponíveis para uso."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM dispositivos WHERE status = 'disponivel' ORDER BY data_registro DESC"
        )
        dispositivos = cursor.fetchall()
        cursor.close()
        conn.close()
        return dispositivos
    except Exception as e:
        print(f"Erro ao buscar dispositivos: {e}")
        return []

@app.route('/api/dispositivo/registro', methods=['POST'])
def registrar_dispositivo_route():
    """
    Rota para registro automático de dispositivos IoT.
    Espera um JSON no formato:
    {
        "dispositivo_id": "string", # MAC address para Arduino ou UUID para Raspberry Pi
        "tipo_equipamento": "arduino" ou "raspberry"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados or not all(k in dados for k in ('dispositivo_id', 'tipo_equipamento')):
            return jsonify({'error': 'Dados incompletos'}), 400
            
        if dados['tipo_equipamento'] not in ['arduino', 'raspberry']:
            return jsonify({'error': 'Tipo de equipamento inválido'}), 400
            
        # Tenta registrar o dispositivo
        sucesso = registrar_dispositivo(dados['dispositivo_id'], dados['tipo_equipamento'])
        
        if sucesso:
            return jsonify({'message': 'Dispositivo registrado com sucesso'}), 201
        else:
            return jsonify({'error': 'Dispositivo já registrado'}), 409
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def registrar_dispositivo(dispositivo_id: str, tipo_equipamento: str) -> bool:
    """
    Registra um novo dispositivo no banco de dados.
    Retorna True se o registro foi bem sucedido, False se o dispositivo já existe.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o dispositivo já existe
        cursor.execute(
            "SELECT id FROM dispositivos WHERE id = %s",
            (dispositivo_id,)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False
            
        # Registra o novo dispositivo
        cursor.execute(
            """
            INSERT INTO dispositivos (id, tipo_equipamento, status, data_registro)
            VALUES (%s, %s, 'disponivel', NOW())
            """,
            (dispositivo_id, tipo_equipamento)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro ao registrar dispositivo: {e}")
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)