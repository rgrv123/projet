from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
import mysql.connector
import bcrypt
import secrets
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1", "http://127.0.0.1:80", "http://localhost", 
                                            "http://localhost:80", "http://127.0.0.1:1337", "http://localhost:1337"],
                                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                                "allow_headers": ["Content-Type", "Authorization"]}})

db_config = {
    "host": "localhost",  
    "user": "root",      
    "password": "",  
    "database": "projet"
}

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.errorhandler(RateLimitExceeded)
def ratelimit_error(e):
    return jsonify({"error": "Trop de requêtes. Veuillez réessayer plus tard."}), 429

@app.route('/api/login', methods=['OPTIONS'])
def handle_login_options():
    return '', 200

@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 200


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Token manquant'}), 401
            
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            query = "SELECT pseudo, expiration FROM sessions WHERE token = %s"
            cursor.execute(query, (token,))
            token_data = cursor.fetchone()
            cursor.close()
            conn.close()

            if not token_data:
                return jsonify({'error': 'Token invalide'}), 401
                
            if datetime.now() > token_data['expiration']:
                return jsonify({'error': 'Token expiré'}), 401

            return f(token_data['pseudo'], *args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return decorated

@app.route('/api/change_password', methods=['POST'])
@limiter.limit("3 per minute")
@token_required
def change_password(current_user):
    try:
        data = request.json
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE pseudo = %s", (current_user,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password = %s WHERE pseudo = %s", (hashed_password, current_user))
            conn.commit()

            if cursor.rowcount > 0:
                return jsonify({"success": True, "message": "Mot de passe changé avec succès"}), 200
            else:
                return jsonify({"success": False, "error": "Erreur lors de la mise à jour du mot de passe"}), 500
        else:
            return jsonify({"success": False, "error": "Mot de passe actuel incorrect"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update_user_data/<string:pseudo>', methods=['POST'])
@limiter.limit("100 per minute")
@token_required
def update_user_data(current_user, pseudo):
    if current_user != pseudo:
        return jsonify({"error": "Non autorisé"}), 403
        
    try:
        data = request.json
        if not ('q1' in data or 'q2' in data):
            return jsonify({"error": "Au moins un champ (q1 ou q2) doit être fourni"}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        updates = []
        values = []

        if 'q1' in data:
            updates.append("q1 = %s")
            values.append(data['q1'])
        if 'q2' in data:
            updates.append("q2 = %s")
            values.append(data['q2'])

        values.append(pseudo)

        query = f"UPDATE users SET {', '.join(updates)} WHERE pseudo = %s"
        cursor.execute(query, tuple(values))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        cursor.close()
        conn.close()

        return jsonify({"message": "Mise à jour réussie"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/update/<int:id_poubelle>', methods=['POST'])
@limiter.limit("100 per minute")
@token_required
def update_poubelle(current_user, id_poubelle):
   try:
       data = request.json

       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor()

       updates = []
       values = []

       if 'volume' in data:
           updates.append("volume = %s")
           values.append(data['volume'])
       if 'temperature' in data:
           updates.append("temperature = %s")
           values.append(data['temperature'])
       if 'poids' in data:
           updates.append("poids = %s")
           values.append(data['poids'])

       if not updates:
           return jsonify({"error": "Aucun champ"}), 400

       values.append(id_poubelle)

       query = f"UPDATE poubelles SET {', '.join(updates)} WHERE id_poubelle = %s"
       cursor.execute(query, tuple(values))
       conn.commit()

       if cursor.rowcount == 0:
           return jsonify({"error": f"Non fait"}), 404

       cursor.close()
       conn.close()
       return jsonify({"message": f"Fait"}), 200
   except Exception as e:
       return jsonify({"error": str(e)}), 500


@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.json
        pseudo = data.get('pseudo')
        mot_de_passe = data.get('mot_de_passe')

        if not pseudo or not mot_de_passe:
            return jsonify({"error": "Pseudo et mot de passe requis"}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE pseudo = %s"
        cursor.execute(query, (pseudo,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        if bcrypt.checkpw(mot_de_passe.encode('utf-8'), user['password'].encode('utf-8')):
            token = secrets.token_hex(32)
            expiration = datetime.now() + timedelta(hours=24)
            
            cursor.execute("DELETE FROM sessions WHERE pseudo = %s", (pseudo,))
            
            cursor.execute(
                "INSERT INTO sessions (token, pseudo, expiration) VALUES (%s, %s, %s)",
                (token, pseudo, expiration)
            )
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Connexion réussie",
                "token": token,
                "user": {"pseudo": pseudo}
            }), 200
        else:
            cursor.close()
            conn.close()
            return jsonify({"error": "Mot de passe incorrect"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@limiter.limit("5 per minute")
@token_required
def logout(current_user):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = %s", (token,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Déconnexion réussie"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_user_by_token', methods=['GET'])
@limiter.limit("100 per minute")
@token_required
def get_user_by_token(current_user):
   try:
       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor(dictionary=True)

       query = "SELECT t.pseudo FROM sessions t WHERE t.token = %s"
       token = request.headers['Authorization'].split(" ")[1]
       cursor.execute(query, (token,))
       result = cursor.fetchone()

       cursor.close()
       conn.close()

       if result:
           return jsonify(result), 200
       else:
           return jsonify({"error": "Token invalide"}), 404
   except Exception as e:
       return jsonify({"error": str(e)}), 500

################################# GETS #################################
@app.route('/api/get_poubelles', methods=['GET'])
@limiter.limit("100 per minute")
@token_required
def get_poubelles(current_user):
   try:
       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor(dictionary=True)

       cursor.execute("SELECT * FROM poubelles")
       results = cursor.fetchall()

       cursor.close()
       conn.close()
       return jsonify(results), 200
   except Exception as e:
       return jsonify({"error": str(e)}), 500


@app.route('/api/get_poubelle_coords/<int:id_poubelle>', methods=['GET'])
@limiter.limit("100 per minute")
@token_required
def get_poubelle_coordinates(current_user, id_poubelle):
   try:
       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor(dictionary=True)

       query = "SELECT x, y, z FROM poubelles WHERE id_poubelle = %s"
       cursor.execute(query, (id_poubelle,))
       result = cursor.fetchone()

       cursor.close()
       conn.close()

       if result:
           return jsonify(result), 200
       else:
           return jsonify({"error": "Poubelle non trouvée"}), 404
   except Exception as e:
       return jsonify({"error": str(e)}), 500

@app.route('/api/get_stats', methods=['GET'])
@limiter.limit("100 per minute")
@token_required
def get_stats(current_user):
   try:
       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor(dictionary=True)

       query = "SELECT COUNT(*) AS poubelles_count FROM poubelles"
       cursor.execute(query)
       poubelles_count = cursor.fetchone()['poubelles_count']

       query = "SELECT SUM(volume) AS total_volume FROM poubelles"
       cursor.execute(query)
       total_volume = cursor.fetchone()['total_volume']

       cursor.close()
       conn.close()

       return jsonify({
           "poubelles_count": poubelles_count,
           "total_volume": total_volume,
       }), 200
   except Exception as e:
       return jsonify({"error": str(e)}), 500


@app.route('/api/get_user_data/<string:pseudo>', methods=['GET'])
@limiter.limit("100 per minute")
@token_required
def get_user_data(current_user, pseudo):
   if current_user != pseudo:
       return jsonify({"error": "Non autorisé"}), 403
       
   try:
       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor(dictionary=True)

       query = "SELECT pseudo, q1, q2 FROM users WHERE pseudo = %s"
       cursor.execute(query, (pseudo,))
       result = cursor.fetchone()

       cursor.close()
       conn.close()

       if result:
           return jsonify(result), 200
       else:
           return jsonify({"error": "Utilisateur non trouvé"}), 404
   except Exception as e:
       return jsonify({"error": str(e)}), 500


@app.route('/api/get_quartiers', methods=['GET'])
@limiter.limit("50 per minute")
@token_required
def get_quartiers(current_user):
   try:
       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor(dictionary=True)

       cursor.execute("SELECT * FROM quartiers")
       results = cursor.fetchall()

       cursor.close()
       conn.close()
       return jsonify(results), 200
   except Exception as e:
       return jsonify({"error": str(e)}), 500

@app.route('/api/get_poubelles/<int:id_quartier>', methods=['GET'])
@limiter.limit("100 per minute")
@token_required
def get_poubelle_by_quartier(current_user, id_quartier):
   try:
       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor(dictionary=True)

       query = "SELECT * FROM poubelles WHERE id_quartier = %s"
       cursor.execute(query, (id_quartier,))
       results = cursor.fetchall()

       cursor.close()
       conn.close()
       return jsonify(results), 200
   except Exception as e:
       return jsonify({"error": str(e)}), 500

@app.route('/api/get_poubelle/<int:id_quartier>', methods=['GET'])
@limiter.limit("100 per minute")
@token_required
def get_poubelles_by_id(current_user, id_quartier):
   try:
       conn = mysql.connector.connect(**db_config)
       cursor = conn.cursor(dictionary=True)

       query = "SELECT * FROM poubelles WHERE id_poubelle = %s"
       cursor.execute(query, (id_quartier,))
       results = cursor.fetchall()

       cursor.close()
       conn.close()
       return jsonify(results), 200
   except Exception as e:
       return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, debug=True)    