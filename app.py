from flask import Flask, render_template, request, redirect
import sqlite3, os, json, csv

app = Flask(__name__)

# Conexión inicial a SQLite

def conectar():
    return sqlite3.connect("inventario.db")

# Crear tabla si no existe
with conectar() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL
        )
    """)
    conn.commit()
# Rutas principales

@app.route('/')
def inicio():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/inventario')
def inventario():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario")
    productos = cursor.fetchall()
    conn.close()
    return render_template("inventario.html", productos=productos)
#NUEVA RUTA: Persistencia
@app.route('/persistencia')
def persistencia():
    return render_template("persistencia.html")

# CRUD: Agregar

@app.route('/agregar', methods=['POST'])
def agregar():
    producto = request.form['producto']
    precio = float(request.form['precio'])
    cantidad = int(request.form['cantidad'])

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventario (producto, precio, cantidad) VALUES (?, ?, ?)",
                   (producto, precio, cantidad))
    conn.commit()
    conn.close()

    return redirect('/inventario')

# CRUD: Editar

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        producto = request.form['producto']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])
        cursor.execute("UPDATE inventario SET producto=?, precio=?, cantidad=? WHERE id=?",
                       (producto, precio, cantidad, id))
        conn.commit()
        conn.close()
        return redirect('/inventario')
    else:
        cursor.execute("SELECT * FROM inventario WHERE id=?", (id,))
        producto = cursor.fetchone()
        conn.close()
        return render_template("editar.html", producto=producto)

# CRUD: Eliminar
@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventario WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/inventario')

# CRUD: Buscar
@app.route('/buscar/<int:id>')
def buscar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario WHERE id=?", (id,))
    producto = cursor.fetchone()
    conn.close()
    return render_template("buscar.html", producto=producto)

# Persistencia en archivos

@app.route('/guardar_archivos', methods=['POST'])
def guardar_archivos():
    nombre = request.form['nombre']
    precio = request.form['precio']
    cantidad = request.form['cantidad']
    ruta_base = "inventario/data/"
    os.makedirs(ruta_base, exist_ok=True)

    # TXT
    with open(ruta_base + "datos.txt", "a", encoding="utf-8") as f:
        f.write(f"{nombre}, {precio}, {cantidad}\n")

    # JSON
    archivo_json = ruta_base + "datos.json"
    datos_json = []
    if os.path.exists(archivo_json):
        with open(archivo_json, "r", encoding="utf-8") as f:
            try:
                datos_json = json.load(f)
            except:
                datos_json = []
    datos_json.append({"nombre": nombre, "precio": precio, "cantidad": cantidad})
    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(datos_json, f, indent=4)

    # CSV
    archivo_csv = ruta_base + "datos.csv"
    existe = os.path.exists(archivo_csv)
    with open(archivo_csv, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["nombre", "precio", "cantidad"])
        writer.writerow([nombre, precio, cantidad])

    return redirect('/datos')

@app.route('/datos')
def datos():
    ruta_base = "inventario/data/"
    datos_txt, datos_json, datos_csv = [], [], []
    if os.path.exists(ruta_base + "datos.txt"):
        with open(ruta_base + "datos.txt", "r", encoding="utf-8") as f:
            datos_txt = f.readlines()
    if os.path.exists(ruta_base + "datos.json"):
        with open(ruta_base + "datos.json", "r", encoding="utf-8") as f:
            try:
                datos_json = json.load(f)
            except:
                datos_json = []
    if os.path.exists(ruta_base + "datos.csv"):
        with open(ruta_base + "datos.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            datos_csv = list(reader)
    return render_template("datos.html", txt=datos_txt, json_datos=datos_json, csv_datos=datos_csv)

# Ejecutar aplicación
if __name__ == '__main__':
    app.run(debug=True)