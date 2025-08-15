import os
import re
import mysql.connector
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, session, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash 
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
import pytz


app = Flask(__name__)
app.secret_key = os.urandom(24) 


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_usuario'  # type: ignore
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


class NotificacaoDict(TypedDict, total=False):
    id: int
    pedido_id: int
    mensagem: str
    data_criacao: datetime
    cpf_usuario: str
    cnpj_empresa: str

def buscar_notificacoes(id_entidade):        #VERIFICAR SE FUNCIONA
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
                return redirect(url_for('dashboard_usuario', cpf=usuario.cpf))
            else:
                
                flash('CPF ou senha incorretos', 'danger')
                return render_template('login_usuario.html')

        cadastro_sucesso = request.args.get('cadastro_sucesso')
        return render_template('login_usuario.html', cadastro_sucesso=cadastro_sucesso)
    except Exception as e:
        
        flash(f'Ocorreu um erro no login. Tente novamente.', 'danger')
        print(f"Erro detalhado no login_usuario: {e}") 
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
                    return render_template('login_empresa.html')

                if check_password_hash(empresa.senha, senha_digitada):
                    login_user(empresa)
                    return redirect(url_for('perfil_empresa', cnpj=empresa.cnpj))
                else:
                    print("check_password_hash retornou False. Senha não coincide.")
                    flash('CNPJ ou senha incorretos', 'danger')
                    return render_template('login_empresa.html')
            else:
                print("Empresa não encontrada no banco de dados.")
                flash('CNPJ ou senha incorretos', 'danger')
                return render_template('login_empresa.html')

        return render_template('login_empresa.html')
    except Exception as e:
        flash(f'Ocorreu um erro no login da empresa. Tente novamente.', 'danger')
        print(f"Erro detalhado no login_empresa: {e}")
        return render_template('login_empresa.html')


@app.route('/logout')
@login_required 
def logout():
    logout_user() 
    flash('Você foi desconectado.', 'info')
    return render_template('index.html')

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
                return render_template('cadastro.html')

            if not re.match(r'^\d{11}$', cpf):
                flash('O CPF deve conter apenas 11 dígitos numéricos', 'danger')
                return render_template('cadastro.html')

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
                return render_template('cadastro.html')
            
            hashed_senha = generate_password_hash(senha)

            query_insert_user = "INSERT INTO usuarios (nome, cpf, email, endereco, senha) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query_insert_user, (nome, cpf, email, endereco, hashed_senha)) 
            conn.commit()
            
            cursor.close()
            conn.close()

            flash('Cadastro realizado com sucesso!', 'success')
            return render_template('login_usuario.html', cadastro_sucesso=True)

        return render_template('cadastro.html')
    except Exception as e:
        flash('Ocorreu um erro ao processar o cadastro. Tente novamente.', 'danger')
        print(f"Erro no cadastro: {e}") 
        return render_template('cadastro.html') 

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
                return render_template('cadastro_empresa.html')

            if len(endereco_empresa) > 255:
                flash('O endereço é muito longo', 'danger')
                return render_template('cadastro_empresa.html')

            if senha_empresa != confirmacao_senha_empresa:
                flash('As senhas não coincidem', 'danger')
                return render_template('cadastro_empresa.html')

            if not re.match(r'^\d{14}$', cnpj):
                flash('O CNPJ deve conter apenas 14 dígitos numéricos', 'danger')
                return render_template('cadastro_empresa.html')

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
                return render_template('cadastro_empresa.html')
            
            
            hashed_senha_empresa = generate_password_hash(senha_empresa)
            
            query_insert_company = "INSERT INTO empresas (nome, cnpj, email, endereco, senha) VALUES (%s, %s, %s, %s, %s)"
            
            cursor.execute(query_insert_company, (nome_empresa, cnpj, email_empresa, endereco_empresa, hashed_senha_empresa))
            conn.commit()
            
            cursor.close()
            conn.close()

            flash('Cadastro realizado com sucesso. Faça o login abaixo.', 'success')
            return render_template('login_empresa.html')

        return render_template('cadastro_empresa.html')
    except Exception as e:
        flash('Ocorreu um erro ao processar o cadastro. Tente novamente.', 'danger')
        print(f"Erro no cadastro_empresa: {e}") 
        return render_template('cadastro_empresa.html')

@app.route('/editar_usuario/<cpf>', methods=['POST'])
@login_required
def editar_usuario_perfil(cpf):
    if not isinstance(current_user, Usuario) or current_user.cpf != cpf:
        flash('Acesso não autorizado para editar este perfil.', 'danger')
        return render_template('dashboard_usuario.html', usuario=current_user)

    nome = request.form.get('nome')
    email = request.form.get('email')
    endereco = request.form.get('endereco')
    senha = request.form.get('senha')

    if not nome or not email or not endereco:
        flash('Nome, email e endereço são obrigatórios!', 'danger')
        return render_template('dashboard_usuario.html', usuario=current_user)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        set_values = []
        params = []
        query = "UPDATE usuarios SET "

        if nome:
            set_values.append("nome = %s")
            params.append(nome)
        if email:
            set_values.append("email = %s")
            params.append(email)
        if endereco:
            set_values.append("endereco = %s")
            params.append(endereco)
        if senha:
            set_values.append("senha = %s")
            params.append(generate_password_hash(senha))

        query += ", ".join(set_values)
        query += " WHERE cpf = %s"
        params.append(cpf)

        cursor.execute(query, tuple(params))
        conn.commit()

        # Atualiza os dados do usuário na sessão
        current_user.nome = nome
        current_user.email = email
        current_user.endereco = endereco

        cursor.close()
        conn.close()

        flash('Perfil atualizado com sucesso!', 'success')
        # Se a requisição for AJAX, retorna status 200
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return '', 200
        return render_template('dashboard_usuario.html', usuario=current_user)
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        flash('Erro ao atualizar o perfil. Tente novamente.', 'danger')
        # Se a requisição for AJAX, retorna status 400
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return '', 400
        return render_template('dashboard_usuario.html', usuario=current_user)

@app.route('/editar_empresa/<cnpj>', methods=['GET', 'POST'])
@login_required
def editar_empresa_perfil(cnpj: str):
    if not isinstance(current_user, Empresa) or current_user.cnpj != cnpj:
        flash('Acesso não autorizado para editar este perfil.', 'danger')
        return render_template('perfil_empresa.html', empresa=current_user)

    nome = request.form.get('nome')
    endereco = request.form.get('endereco')
    senha = request.form.get('senha')

    if not nome or not endereco:
        flash('Nome e endereço são obrigatórios!', 'danger')
        return render_template('perfil_empresa.html', empresa=current_user)

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
    return render_template('perfil_empresa.html', empresa=current_user)

@app.route('/perfil_empresa/<cnpj>') 
@login_required
def perfil_empresa(cnpj): 
    try:
        if not current_user.is_an_empresa():
            print(f"current_user não é uma empresa. Tipo: {type(current_user)}")
            flash('Acesso não autorizado.', 'danger')
            logout_user() 
            return redirect(url_for('login_usuario')) 
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Dispositivos fixos
        dispositivos = [
            {'dispositivo_id': 1, 'dispositivo': 'Arduino'},
            {'dispositivo_id': 2, 'dispositivo': 'ESP32'},
            {'dispositivo_id': 3, 'dispositivo': 'Raspberry'},
        ]

        ph_por_dispositivo = {}
        nivel_por_dispositivo = {}
        for disp in dispositivos:
            dispositivo_id = disp['dispositivo_id']
            dispositivo_nome = disp['dispositivo']
            # pH atual
            cursor.execute("""
                SELECT * FROM ph_niveis WHERE dispositivo_id = %s ORDER BY data DESC LIMIT 1
            """, (dispositivo_id,))
            ph_atual = convert_row_to_dict(cursor.fetchone())
            # Histórico pH
            cursor.execute("""
                SELECT * FROM ph_niveis WHERE dispositivo_id = %s ORDER BY data DESC LIMIT 5
            """, (dispositivo_id,))
            historico_ph = [convert_row_to_dict(row) for row in cursor.fetchall()]
            ph_por_dispositivo[dispositivo_nome] = {'atual': ph_atual, 'historico': historico_ph}
            # Nível atual
            cursor.execute("""
                SELECT * FROM niveis_agua WHERE dispositivo_id = %s ORDER BY data DESC LIMIT 1
            """, (dispositivo_id,))
            nivel_atual = convert_row_to_dict(cursor.fetchone())
            # Histórico nível
            cursor.execute("""
                SELECT * FROM niveis_agua WHERE dispositivo_id = %s ORDER BY data DESC LIMIT 5
            """, (dispositivo_id,))
            historico_nivel = [convert_row_to_dict(row) for row in cursor.fetchall()]
            nivel_por_dispositivo[dispositivo_nome] = {'atual': nivel_atual, 'historico': historico_nivel}

        notificacoes = buscar_notificacoes(current_user.cnpj)
        comunicados_gerais = buscar_comunicado_geral()
        pedidos = buscar_pedidos_por_empresa(current_user.cnpj)
        
        cursor.close()
        conn.close()

        return render_template(
            'perfil_empresa.html',
            company=current_user,
            dispositivos=dispositivos,
            ph_por_dispositivo=ph_por_dispositivo,
            nivel_por_dispositivo=nivel_por_dispositivo,
            notificacoes=notificacoes,
            comunicados_gerais=comunicados_gerais,
            pedidos=pedidos,
        )
    except Exception as e:
        print(f"ERRO CRÍTICO ao renderizar perfil_empresa: {e}") 
        flash('Ocorreu um erro ao carregar o perfil da empresa. Tente novamente.', 'danger')
        logout_user() 
        return redirect(url_for('login_empresa'))


@app.route('/dashboard_usuario/<cpf>')
@login_required
def dashboard_usuario(cpf):
    if not isinstance(current_user, Usuario) or current_user.cpf != cpf:
        flash('Acesso não autorizado.', 'danger')
        return render_template('pagina_inicial.html')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Busca pedidos
        query_pedidos = """
            SELECT p.*, u.nome AS usuario_nome
            FROM pedidos p
            JOIN usuarios u ON p.cpf_usuario = u.cpf
            WHERE p.cpf_usuario = %s
            ORDER BY p.data DESC
        """
        cursor.execute(query_pedidos, (cpf,))
        pedidos = [convert_row_to_dict(row) for row in cursor.fetchall()]

        # Busca comunicados dos pedidos
        query_comunicados = """
            SELECT cp.*, p.descricao AS pedido_descricao
            FROM comunicado_pedido cp
            JOIN pedidos p ON cp.pedido_id = p.id
            WHERE p.cpf_usuario = %s
            ORDER BY cp.data DESC
        """
        cursor.execute(query_comunicados, (cpf,))
        comunicados = [convert_row_to_dict(row) for row in cursor.fetchall()]

        # Busca comunicados gerais
        query_comunicados_gerais = """
            SELECT * FROM comunicados_gerais
            ORDER BY data DESC
        """
        cursor.execute(query_comunicados_gerais)
        comunicados_gerais = [convert_row_to_dict(row) for row in cursor.fetchall()]

        # Busca lista de empresas
        query_empresas = "SELECT cnpj, nome FROM empresas"
        cursor.execute(query_empresas)
        empresas = [convert_row_to_dict(row) for row in cursor.fetchall()]

        # Dispositivos fixos
        dispositivos = [
            {'dispositivo_id': 1, 'dispositivo': 'Arduino'},
            {'dispositivo_id': 2, 'dispositivo': 'ESP32'},
            {'dispositivo_id': 3, 'dispositivo': 'Raspberry'},
        ]

        ph_por_dispositivo = {}
        nivel_por_dispositivo = {}
        for disp in dispositivos:
            dispositivo_id = disp['dispositivo_id']
            dispositivo_nome = disp['dispositivo']
            # pH atual
            cursor.execute("""
                SELECT * FROM ph_niveis WHERE dispositivo_id = %s ORDER BY data DESC LIMIT 1
            """, (dispositivo_id,))
            ph_atual = convert_row_to_dict(cursor.fetchone())
            # Histórico pH
            cursor.execute("""
                SELECT * FROM ph_niveis WHERE dispositivo_id = %s ORDER BY data DESC LIMIT 5
            """, (dispositivo_id,))
            historico_ph = [convert_row_to_dict(row) for row in cursor.fetchall()]
            ph_por_dispositivo[dispositivo_nome] = {'atual': ph_atual, 'historico': historico_ph}
            # Nível atual
            cursor.execute("""
                SELECT * FROM niveis_agua WHERE dispositivo_id = %s ORDER BY data DESC LIMIT 1
            """, (dispositivo_id,))
            nivel_atual = convert_row_to_dict(cursor.fetchone())
            # Histórico nível
            cursor.execute("""
                SELECT * FROM niveis_agua WHERE dispositivo_id = %s ORDER BY data DESC LIMIT 5
            """, (dispositivo_id,))
            historico_nivel = [convert_row_to_dict(row) for row in cursor.fetchall()]
            nivel_por_dispositivo[dispositivo_nome] = {'atual': nivel_atual, 'historico': historico_nivel}

        cursor.close()
        conn.close()

        return render_template('dashboard_usuario.html',
                             usuario=current_user,
                             pedidos=pedidos,
                             comunicados=comunicados,
                             comunicados_gerais=comunicados_gerais,
                             dispositivos=dispositivos,
                             ph_por_dispositivo=ph_por_dispositivo,
                             nivel_por_dispositivo=nivel_por_dispositivo,
                             empresas=empresas)
    except Exception as e:
        flash(f'Erro ao carregar o dashboard: {str(e)}', 'danger')
        return render_template('pagina_inicial.html')



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
    


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.template_filter('dateformat')
def dateformat(value, format="%d/%m/%Y %H:%M"):
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return value
    try:
        # Tenta converter para timezone de São Paulo
        if value.tzinfo is None:
            value = value.replace(tzinfo=pytz.UTC)
        value = value.astimezone(pytz.timezone('America/Sao_Paulo'))
    except Exception:
        # Se der erro, faz ajuste manual de -3h
        value = value - timedelta(hours=3)
    return value.strftime(format)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)