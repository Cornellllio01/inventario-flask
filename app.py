from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sys

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_123456'

# Função para converter valores em inteiros de forma segura
def to_int(valor):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 0

# Inicialização do Supabase
supabase = None
connection_error = None

try:
    from supabase import create_client, Client

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
        if not supabase or connection_error:
            return f"""
            <h1>Erro de Configuração</h1>
            <p><strong>Problema:</strong> {connection_error or 'Supabase não inicializado'}</p>
            <p><strong>Solução:</strong> Configure as variáveis SUPABASE_URL e SUPABASE_KEY no ambiente</p>
            <a href="/teste-conexao">Testar Conexão</a>
            """

        resultado = supabase.table("inventario_novo").select("*").execute()
        inventario = resultado.data if resultado.data else []

        # Calculando os totais de cada equipamento
        totais = {
            "pc": 0, "notebooks": 0, "monitores": 0, "mouses": 0,
            "teclados": 0, "webcams": 0, "hd": 0, "projetores": 0
        }

        for item in inventario:
            for chave in totais.keys():
                totais[chave] += item.get(chave, 0) or 0

        return render_template("index.html", equipamentos=inventario, totais=totais)

    except Exception as e:
        print(f"❌ Erro na rota index: {e}")
        return f"""
        <h1>Erro na Aplicação</h1>
        <p><strong>Erro:</strong> {str(e)}</p>
        <p>Verifique os logs para mais detalhes.</p>
        <a href="/teste-conexao">Testar Conexão</a>
        """

@app.route("/adicionar", methods=["POST"])
def adicionar():
    try:
        if not supabase:
            return jsonify({"erro": "Conexão com Supabase não disponível"}), 500

        comodo = request.form.get("comodo")
        if not comodo:
            return jsonify({"erro": "Campo 'comodo' é obrigatório"}), 400

        dados = {
            "comodo": comodo,
            "pc": to_int(request.form.get("pc")),
            "notebooks": to_int(request.form.get("notebooks")),
            "monitores": to_int(request.form.get("monitores")),
            "mouses": to_int(request.form.get("mouses")),
            "teclados": to_int(request.form.get("teclados")),
            "webcams": to_int(request.form.get("webcams")),
            "hd": to_int(request.form.get("hd")),
            "projetores": to_int(request.form.get("projetores"))
        }

        print(f"🔄 Tentando inserir: {dados}")

        resultado = supabase.table("inventario_novo").insert(dados).execute()

        print(f"✅ Inserção bem-sucedida: {resultado}")
        return redirect(url_for("index"))

    except Exception as e:
        print(f"❌ Erro ao inserir: {e}")
        return f"Erro ao adicionar equipamento: {str(e)}", 500

@app.route("/teste-conexao")
def teste_conexao():
    try:
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

        resultado = supabase.table("inventario_novo").select("*", count="exact").execute()

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
