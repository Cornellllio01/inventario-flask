from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sys

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_super_secreta_default")

# Função para converter valores em int com segurança
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

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        connection_error = "Variáveis SUPABASE_URL e SUPABASE_KEY precisam estar configuradas"
        print(f"❌ {connection_error}")
    else:
        supabase: Client = create_client(url, key)
        print("✅ Cliente Supabase criado com sucesso")

except ImportError as e:
    connection_error = f"Erro ao importar supabase: {e}"
    print(f"❌ {connection_error}")
except Exception as e:
    connection_error = f"Erro na conexão com Supabase: {e}"
    print(f"❌ {connection_error}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return adicionar()

    if connection_error or not supabase:
        return f"""
            <h1>Erro de Configuração</h1>
            <p>{connection_error or 'Supabase não inicializado'}</p>
            <p>Configure as variáveis SUPABASE_URL e SUPABASE_KEY no ambiente.</p>
            """

    try:
        resultado = supabase.table("inventario_novo").select("*").execute()
        equipamentos = resultado.data or []

        # Calcula os totais
        totais = {
            "pc": sum(to_int(e.get("pc")) for e in equipamentos),
            "notebook": sum(to_int(e.get("notebook")) for e in equipamentos),
            "monitore": sum(to_int(e.get("monitore")) for e in equipamentos),
            "mouse": sum(to_int(e.get("mouse")) for e in equipamentos),
            "teclado": sum(to_int(e.get("teclado")) for e in equipamentos),
            "webcam": sum(to_int(e.get("webcam")) for e in equipamentos),
            "hd": sum(to_int(e.get("hd")) for e in equipamentos),
            "projetore": sum(to_int(e.get("projetore")) for e in equipamentos),
        }

        return render_template("index.html", equipamentos=equipamentos, totais=totais)

    except Exception as e:
        print(f"❌ Erro na rota index: {e}")
        return f"<h1>Erro na Aplicação</h1><p>{str(e)}</p>"

@app.route("/adicionar", methods=["POST"])
def adicionar():
    if connection_error or not supabase:
        return "Erro de configuração do Supabase", 500

    comodo = request.form.get("comodo")
    if not comodo:
        return "Campo 'comodo' é obrigatório", 400

    dados = {
        "comodo": comodo,
        "pc": to_int(request.form.get("pc")),
        "notebooks": to_int(request.form.get("notebooks")),
        "monitores": to_int(request.form.get("monitores")),
        "mouses": to_int(request.form.get("mouses")),
        "teclados": to_int(request.form.get("teclados")),
        "webcams": to_int(request.form.get("webcams")),
        "hd": to_int(request.form.get("hd")),
        "projetores": to_int(request.form.get("projetores")),
    }

    try:
        supabase.table("inventario_novo").insert(dados).execute()
        return redirect(url_for("index"))
    except Exception as e:
        print(f"❌ Erro ao inserir: {e}")
        return f"Erro ao adicionar equipamento: {str(e)}", 500

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    try:
        resultado = supabase.table("inventario_novo").select("*").execute()
        equipamentos = resultado.data or []

        if index < 0 or index >= len(equipamentos):
            return "Índice inválido", 404

        # Supabase não tem delete por índice direto, precisamos identificar o ID do registro
        item = equipamentos[index]
        id_registro = item.get("id")  # Assume que sua tabela tem coluna 'id' como PK

        if not id_registro:
            return "Registro sem ID não pode ser deletado", 400

        supabase.table("inventario_novo").delete().eq("id", id_registro).execute()

        return redirect(url_for("index"))

    except Exception as e:
        print(f"❌ Erro ao deletar: {e}")
        return f"Erro ao deletar equipamento: {str(e)}", 500

@app.route("/teste-conexao")
def teste_conexao():
    info = {
        "supabase_inicializado": supabase is not None,
        "connection_error": connection_error,
        "supabase_url": os.environ.get("SUPABASE_URL", "NÃO CONFIGURADA"),
        "supabase_key_exists": bool(os.environ.get("SUPABASE_KEY")),
        "python_version": sys.version,
    }
    try:
        if not supabase:
            return jsonify({
                "status": "ERRO",
                "info": info
            })
        resultado = supabase.table("inventario_novo").select("id", count="exact").execute()

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
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
