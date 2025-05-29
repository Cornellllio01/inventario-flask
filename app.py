from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client
from datetime import datetime

app = Flask(__name__)

# 🔗 Configuração do Supabase
url = "https://lxrzmysrrcqcabhxfeti.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx4cnpteXNycmNxY2FiaHhmZXRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgzNDk3MzAsImV4cCI6MjA2MzkyNTczMH0.UE-nVgvSZjX4I4E5AB1sAAdCOaK46C4I2aYkDhn52dA"
supabase: Client = create_client(url, key)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        comodo = request.form.get("comodo")
        pcs = int(request.form.get("pcs", 0))
        notebooks = int(request.form.get("notebooks", 0))
        monitores = int(request.form.get("monitores", 0))
        mouses = int(request.form.get("mouses", 0))
        teclados = int(request.form.get("teclados", 0))
        webcams = int(request.form.get("webcams", 0))
        hds = int(request.form.get("hds", 0))
        projetores = int(request.form.get("projetores", 0))
        created_at = datetime.utcnow().isoformat()

        dados = {
            "created_at": created_at,
            "comodo": comodo,
            "pcs": pcs,
            "notebooks": notebooks,
            "monitores": monitores,
            "mouses": mouses,
            "teclados": teclados,
            "webcams": webcams,
            "hds": hds,
            "projetores": projetores
        }

        supabase.table("inventario_novo").insert(dados).execute()
        return redirect(url_for("index"))

    resultado = supabase.table("inventario_novo").select("*").execute()
    inventario = resultado.data if resultado.data else []

    return render_template("index.html", inventario=inventario)

if __name__ == "__main__":
    app.run(debug=True)
