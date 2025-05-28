from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

# 🔧 Configure aqui sua conexão com o banco de dados
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="sua_senha",
    host="localhost",  # ou o host do seu container/postgres
    port="5432"
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        def to_int(value):
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0

        novo = {
            'comodo': request.form.get('comodo', '').strip(),
            'pc': to_int(request.form.get('pc')),
            'notebook': to_int(request.form.get('notebook')),
            'monitor': to_int(request.form.get('monitor')),
            'mouse': to_int(request.form.get('mouse')),
            'teclado': to_int(request.form.get('teclado')),
            'webcam': to_int(request.form.get('webcam')),
            'hd': to_int(request.form.get('hd')),
            'projetor': to_int(request.form.get('projetor'))
        }

        if novo['comodo']:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO equipamentos 
                (comodo, pc, notebook, monitor, mouse, teclado, webcam, hd, projetor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                novo['comodo'], novo['pc'], novo['notebook'], novo['monitor'],
                novo['mouse'], novo['teclado'], novo['webcam'],
                novo['hd'], novo['projetor']
            ))
            conn.commit()
            cur.close()
        return redirect('/')

    # 🔄 Carrega todos os registros do banco
    cur = conn.cursor()
    cur.execute("SELECT comodo, pc, notebook, monitor, mouse, teclado, webcam, hd, projetor FROM equipamentos")
    rows = cur.fetchall()
    cur.close()

    equipamentos = []
    for row in rows:
        equipamentos.append({
            'comodo': row[0],
            'pc': row[1],
            'notebook': row[2],
            'monitor': row[3],
            'mouse': row[4],
            'teclado': row[5],
            'webcam': row[6],
            'hd': row[7],
            'projetor': row[8]
        })

    totais = {
        'pc': sum(item['pc'] for item in equipamentos),
        'notebook': sum(item['notebook'] for item in equipamentos),
        'monitor': sum(item['monitor'] for item in equipamentos),
        'mouse': sum(item['mouse'] for item in equipamentos),
        'teclado': sum(item['teclado'] for item in equipamentos),
        'webcam': sum(item['webcam'] for item in equipamentos),
        'hd': sum(item['hd'] for item in equipamentos),
        'projetor': sum(item['projetor'] for item in equipamentos)
    }

    return render_template('index.html', equipamentos=equipamentos, totais=totais)

@app.route('/delete/<int:index>', methods=['POST'])
def delete_item(index):
    cur = conn.cursor()
    cur.execute("DELETE FROM equipamentos WHERE ctid IN (SELECT ctid FROM equipamentos LIMIT 1 OFFSET %s)", (index,))
    conn.commit()
    cur.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
