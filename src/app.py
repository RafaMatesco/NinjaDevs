from flask import Flask, session, redirect, url_for, render_template, request, flash
from cryptography.fernet import Fernet
import secrets
import json
import os
import bcrypt

from back.user import usuarios_bp
from back.atestados import atestados_bp

key = Fernet.generate_key() # Gera a chave de criptografia
cipher_suite = Fernet(key)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_json  = os.path.join(BASE_DIR, 'back/JSON/users.json')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Cria a pasta se ela não existir

def carregar_usuarios(): # Função para carregar os usuários cadastrados
    try:
        with open(caminho_json, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo) # retorna os users salvos no JSON
    except FileNotFoundError:
        return {}  # Retorna um dic vazio se o arquivo não existir

def verifyLogin(route):
    if session.get("RA"): # verifica se o user está logado
        return render_template(route) # se tiver, envia para a rota especificada
    else:
        return redirect(url_for("login")) # se nao estiver logado, vai para pagina de login


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
    
@app.route('/') # isso define uma rota
def home(): # funcao que é executada quando está na rota
   return verifyLogin("index.html") #envia o caminho do arquivo para a função verifyLogin
    
@app.route('/atestados/')
def atestado():
    return verifyLogin("atestados.html")

@app.route('/equipe/')
def avaliacao():
    return verifyLogin("equipe.html")

@app.route('/login/', methods=["GET","POST"])
def login():
    if request.method == "POST":
        # Captura os dados do formulário
        ra = request.form["login"]
        senha = request.form["senha"]
        
        usuarios = carregar_usuarios()  # Carrega os usuários do JSON
        for user in usuarios:
            if ra == user['ra']: # Verifica se algum user tem o RA digitado
                senha = senha.encode('utf-8')
                senha_armazenada = user["senha"].encode('utf-8')  # Converter para bytes
                
                if bcrypt.checkpw(senha, senha_armazenada): # Comparar senha digitada com a senha no JSON
                    session["RA"] = ra  # Armazena o RA na sessão
                    flash("Login realizado com sucesso!", "success") # toast para mostrar na tela
                    return redirect(url_for("home"))
        
        flash("RA ou senha incorretos!", "danger")  # toast para mostrar na tela
        return redirect(url_for("home"))
    
    return render_template('/user/login.html')

@app.route('/cadastro/')
def cadastro():
    if(session.get("RA") and session.get("senha")): # verifica se o existe o login e senha do user na sessão atual
        return render_template(url_for("home")) # se tiver, envia para a rota do parametro
    else:
        return render_template("/user/cadastro.html") 
    

@app.route("/logout/")
def logout():
    session.clear()  # Remove todos os dados da sessão
    return redirect(url_for("home"))


# Pega as rotas da parte de controlar usuarios e adiciona o prefixo /usuario
app.register_blueprint(usuarios_bp, url_prefix="/usuario")
app.register_blueprint(atestados_bp, url_prefix="/atestado/")

if __name__ == '__main__':
    app.run(debug=True)
