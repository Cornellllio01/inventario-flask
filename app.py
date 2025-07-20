from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_super_secreta_default")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1379")  # senha padrão

# Converte para int com fallback em 0
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
    else:
        supabase: Client = create_client(url, key)
except Exception as e:
    connection_error = str(e)

# Decorator para proteger rotas com login
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        senha = request.form.get("senha")
        if senha == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            error = "Senha incorreta, tente novamente."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        return adicionar()

    if connection_error or not supabase:
        return f"<h1>Erro de Configuração</h1><p>{connection_error}</p>", 500

    # Busca registros
    res = supabase.table("inventario_novo").select("*").execute()
    equipamentos = res.data or []

    # Calcula totais com chaves plurais
    totais = {
        "pc":        sum(to_int(e.get("pc"))         for e in equipamentos),
        "notebooks": sum(to_int(e.get("notebooks"))  for e in equipamentos),
        "monitores": sum(to_int(e.get("monitores"))  for e in equipamentos),
        "mouses":    sum(to_int(e.get("mouses"))     for e in equipamentos),
        "teclados":  sum(to_int(e.get("teclados"))   for e in equipamentos),
        "webcams":   sum(to_int(e.get("webcams"))    for e in equipamentos),
        "hd":        sum(to_int(e.get("hd"))         for e in equipamentos),
        "projetores":sum(to_int(e.get("projetores")) for e in equipamentos),
    }

    return render_template("index.html",
                           equipamentos=equipamentos,
                           totais=totais)

@app.route("/adicionar", methods=["POST"])
@login_required
def adicionar():
    comodo = request.form.get("comodo")
    if not comodo:
        return "Campo 'comodo' é obrigatório", 400

    dados = {
        "comodo":    comodo,
        "pc":        to_int(request.form.get("pc")),
        "notebooks": to_int(request.form.get("notebooks")),
        "monitores": to_int(request.form.get("monitores")),
        "mouses":    to_int(request.form.get("mouses")),
        "teclados":  to_int(request.form.get("teclados")),
        "webcams":   to_int(request.form.get("webcams")),
        "hd":        to_int(request.form.get("hd")),
        "projetores":to_int(request.form.get("projetores")),
    }
    supabase.table("inventario_novo").insert(dados).execute()
    return redirect(url_for("index"))

# NOVA ROTA: Buscar dados para edição (AJAX)
@app.route("/get_equipamento/<int:id>")
@login_required
def get_equipamento(id):
    try:
        res = supabase.table("inventario_novo").select("*").eq("id", id).execute()
        if res.data:
            return jsonify(res.data[0])
        else:
            return jsonify({"error": "Equipamento não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NOVA ROTA: Atualizar equipamento
@app.route("/atualizar/<int:id>", methods=["POST"])
@login_required
def atualizar(id):
    try:
        comodo = request.form.get("comodo")
        if not comodo:
            return jsonify({"error": "Campo 'comodo' é obrigatório"}), 400

        dados = {
            "comodo":    comodo,
            "pc":        to_int(request.form.get("pc")),
            "notebooks": to_int(request.form.get("notebooks")),
            "monitores": to_int(request.form.get("monitores")),
            "mouses":    to_int(request.form.get("mouses")),
            "teclados":  to_int(request.form.get("teclados")),
            "webcams":   to_int(request.form.get("webcams")),
            "hd":        to_int(request.form.get("hd")),
            "projetores":to_int(request.form.get("projetores")),
        }
        
        res = supabase.table("inventario_novo").update(dados).eq("id", id).execute()
        
        if res.data:
            return jsonify({"success": True, "message": "Equipamento atualizado com sucesso"})
        else:
            return jsonify({"error": "Erro ao atualizar equipamento"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    supabase.table("inventario_novo").delete().eq("id", id).execute()
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)