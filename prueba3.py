from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# === CONFIGURACIÓN FIREBASE ===
import json, os
from io import StringIO

firebase_json = os.getenv("FIREBASE_JSON")
if not firebase_json:
    raise ValueError("FIREBASE_JSON no está configurado en las variables de entorno")

cred = credentials.Certificate(json.load(StringIO(firebase_json)))

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://recicla-4ca43-default-rtdb.firebaseio.com/'
})

app = Flask(__name__) 

CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers="*", supports_credentials=True)

#----------------------------------------------------------------------------------
# trabajo
# === FUNCIÓN: CONSULTAR USUARIO ===
@app.route('/consulta/<user_id>', methods=['GET'])
def consulta(user_id):
    ref = db.reference(f"usuarios/{user_id}")
    usuario = ref.get()

    if usuario is None:
        return jsonify({"error": f"El usuario con ID '{user_id}' no existe"}), 404

    # Obtener valores numéricos (asegurando que no sean None)
    lata = int(usuario.get("lata", 0))
    vidrio = int(usuario.get("vidrio", 0))
    tetra = int(usuario.get("tetra", 0))

    # Calcular el total
    total = lata + vidrio + tetra

    return jsonify({
        "user_id": user_id,
        "nombre": usuario.get("nombre", "Desconocido"),
        "lata": lata,
        "vidrio": vidrio,
        "tetra": tetra,
        "total": total
    }), 200

@app.route('/sumar/<user_id>/<categoria>', methods=['GET', 'POST'])
def sumar(user_id, categoria):
    # Verificar que la categoría sea válida
    if categoria not in ["lata", "vidrio", "tetra"]:
        return jsonify({"error": "Categoría inválida. Usa 'lata', 'vidrio' o 'tetra'."}), 400

    # Referencia a Firebase
    ref = db.reference(f"usuarios/{user_id}")
    usuario = ref.get()

    if usuario is None:
        return jsonify({"error": f"El usuario con ID '{user_id}' no existe"}), 404

    # Obtener valor actual de la categoría y sumar 1
    valor_actual = int(usuario.get(categoria, 0))
    nuevo_valor = valor_actual + 1

    # Actualizar el valor en Firebase
    ref.update({categoria: nuevo_valor})

    return jsonify({
        "categoria_actualizada": categoria,
        "nuevo_valor": nuevo_valor
    }), 200

# === FUNCIÓN: CREAR USUARIO ===
@app.route('/crear_usuario/<user_id>/<nombre>', methods=['GET'])
def crear_usuario(user_id, nombre):
    ref = db.reference(f"usuarios/{user_id}")

    # Verificar si el usuario ya existe
    if ref.get() is not None:
        return jsonify({"error": f"El usuario con ID '{user_id}' ya existe"}), 400

    # Crear nuevo usuario
    nuevo_usuario = {
        "nombre": nombre,
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vidrio": 0,
        "lata": 0,
        "tetra": 0
    }

    ref.set(nuevo_usuario)
    return jsonify({
        "usuario": nuevo_usuario
    }), 201

# === FUNCIÓN AUXILIAR PARA OBTENER USUARIOS ===
def obtener_usuarios():
    ref = db.reference("usuarios")
    usuarios = ref.get()
    if not usuarios:
        return {}
    return usuarios


# === TOP LATAS ===
@app.route('/top_latas', methods=['GET'])
def top_latas():
    usuarios = obtener_usuarios()
    if not usuarios:
        return jsonify({"error": "No hay usuarios en la base de datos"}), 404

    ranking = []
    for uid, data in usuarios.items():
        ranking.append({
            "user_id": uid,
            "nombre": data.get("nombre", "Desconocido"),
            "latas": int(data.get("lata", 0))
        })

    ranking_ordenado = sorted(ranking, key=lambda x: x["latas"], reverse=True)[:100]
    return jsonify(ranking_ordenado), 200


# === TOP VIDRIO ===
@app.route('/top_vidrio', methods=['GET'])
def top_vidrio():
    usuarios = obtener_usuarios()
    if not usuarios:
        return jsonify({"error": "No hay usuarios en la base de datos"}), 404

    ranking = []
    for uid, data in usuarios.items():
        ranking.append({
            "user_id": uid,
            "nombre": data.get("nombre", "Desconocido"),
            "vidrio": int(data.get("vidrio", 0))
        })

    ranking_ordenado = sorted(ranking, key=lambda x: x["vidrio"], reverse=True)[:100]
    return jsonify(ranking_ordenado), 200


# === TOP TETRA ===
@app.route('/top_tetra', methods=['GET'])
def top_tetra():
    usuarios = obtener_usuarios()
    if not usuarios:
        return jsonify({"error": "No hay usuarios en la base de datos"}), 404

    ranking = []
    for uid, data in usuarios.items():
        ranking.append({
            "user_id": uid,
            "nombre": data.get("nombre", "Desconocido"),
            "tetra": int(data.get("tetra", 0))
        })

    ranking_ordenado = sorted(ranking, key=lambda x: x["tetra"], reverse=True)[:100]
    return jsonify(ranking_ordenado), 200


# === TOP TOTAL (suma de lata + vidrio + tetra) ===
@app.route('/top_total', methods=['GET'])
def top_total():
    usuarios = obtener_usuarios()
    if not usuarios:
        return jsonify({"error": "No hay usuarios en la base de datos"}), 404

    ranking = []
    for uid, data in usuarios.items():
        lata = int(data.get("lata", 0))
        vidrio = int(data.get("vidrio", 0))
        tetra = int(data.get("tetra", 0))
        total = lata + vidrio + tetra

        ranking.append({
            "user_id": uid,
            "nombre": data.get("nombre", "Desconocido"),
            "total": total
        })

    ranking_ordenado = sorted(ranking, key=lambda x: x["total"], reverse=True)[:100]
    return jsonify(ranking_ordenado), 200

#----------------------------------------------------------------------------------

# # === FUNCIÓN: ACTUALIZAR VALORES ===
# @app.route('/actualizar_usuario/<user_id>', methods=['PUT'])
# def actualizar_valores(user_id):
#     data = request.get_json()
#     lata = data.get("lata")
#     vidrio = data.get("vidrio")
#     tetra = data.get("tetra")

#     ref = db.reference(f"usuarios/{user_id}")
#     if ref.get() is None:
#         return jsonify({"error": f"El usuario con ID '{user_id}' no existe"}), 404

#     datos = {}
#     if lata is not None:
#         datos["lata"] = lata
#     if vidrio is not None:
#         datos["vidrio"] = vidrio
#     if tetra is not None:
#         datos["tetra"] = tetra

#     if not datos:
#         return jsonify({"error": "No se proporcionaron valores para actualizar"}), 400

#     ref.update(datos)
#     return jsonify({"mensaje": f"Usuario {user_id} actualizado", "nuevos_valores": datos}), 200


# === INICIO DEL SERVIDOR ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

