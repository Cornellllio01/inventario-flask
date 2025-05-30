from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_123456'

# Inicialização do Supabase com tratamento de erro
supabase = None
connection_error = None

try:
    from supabase import create_client, Client
    
    # Configuração com fallback
    url = os.environ.get("SUPABASE_URL", "https://lxrzmysrrcqcabhxfeti.supabase.co")
    key = os.environ.get("SUPABASE_KEY")
    
    if not key:
        connection_error = "SUPABASE_KEY não encontrada nas variáveis de ambiente"
        print(f"❌ ERRO: {connection_error}")
    else:
        supabase: Client = create_client(url, key)
        print("✅ Supabase cliente criado com sucesso")
        
except ImportError as e:
    connection_error = f"Erro ao importar supabase: {e}"
    print(f"❌ ERRO DE IMPORTAÇÃO: {connection_error}")
except Exception as e:
    connection_error = f"Erro ao conectar com Supabase: {e}"
    print(f"❌ ERRO DE CONEXÃO: {connection_error}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return adicionar()
    
    try:
        # Se não tem conexão com Supabase, mostra erro
        if not supabase or connection_error:
            return f"""
            <h1>Erro de Configuração</h1>
            <p><strong>Problema:</strong> {connection_error or 'Supabase não inicializado'}</p>
            <p><strong>Solução:</strong> Configure as variáveis SUPABASE_URL e SUPABASE_KEY no Render</p>
            <a href="/teste-conexao">Testar Conexão</a>
            """
        
        # Tentar carregar dados
        resultado = supabase.table("inventario_novo").select("*").execute()
        inventario = resultado.data if resultado.data else []
        
        return render_template("index.html", equipamentos=inventario)
        
    except Exception as e:
        print(f"❌ Erro na rota index: {e}")
        return f"""
        <h1>Erro na Aplicação</h1>
        <p><strong>Erro:</strong> {str(e)}</p>
        <p>Verifique os logs do Render para mais detalhes</p>
        <a href="/teste-conexao">Testar Conexão</a>
        """

@app.route("/adicionar", methods=["POST"])
def adicionar():
    try:
        if not supabase:
            return jsonify({"erro": "Conexão com Supabase não disponível"}), 500
            
        # Coletando dados do formulário
        comodo = request.form.get("comodo")
        if not comodo:
            return jsonify({"erro": "Campo 'comodo' é obrigatório"}), 400
            
        dados = {
            "comodo": comodo,
            "pc": int(request.form.get("pc") or 0),
            "notebook": int(request.form.get("notebook", 0)),
            "monitor": int(request.form.get("monitor", 0)),
            "mouse": int(request.form.get("mouse", 0)),
            "teclado": int(request.form.get("teclado", 0)),
            "webcam": int(request.form.get("webcam", 0)),
            "hd": int(request.form.get("hd", 0)),
            "projetor": int(request.form.get("projetor", 0))
        }
        
        print(f"🔄 Tentando inserir: {dados}")
        
        # Inserção no Supabase
        resultado = supabase.table("inventario_novo").insert(dados).execute()
        
        print(f"✅ Inserção bem-sucedida: {resultado}")
        return redirect(url_for("index"))
        
    except Exception as e:
        print(f"❌ Erro ao inserir: {e}")
        return f"Erro ao adicionar equipamento: {str(e)}", 500

@app.route("/teste-conexao")
def teste_conexao():
    try:
        # Informações de debug
        info = {
            "supabase_inicializado": supabase is not None,
            "connection_error": connection_error,
            "supabase_url": os.environ.get("SUPABASE_URL", "NÃO CONFIGURADA"),
            "supabase_key_exists": bool(os.environ.get("SUPABASE_KEY")),
            "python_version": sys.version,
        }
        
        if not supabase:
            return jsonify({
                "status": "ERRO",
                "info": info
            })
        
        # Teste de conexão
        resultado = supabase.table("inventario_novo").select("count", count="exact").execute()
        
        return jsonify({
            "status": "SUCESSO",
            "total_registros": resultado.count,
            "info": info
        })
        
    except Exception as e:
        return jsonify({
            "status": "ERRO",
            "erro": str(e),
            "info": info
        })

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
