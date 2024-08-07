from flask import Flask, jsonify, request
import mysql.connector
import traceback
import jwt
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'localhost',
    'user': 'root',  
    'password': '', 
    'database': 'dbcuc' 
}

# Conexión a la base de datos
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/register', methods=['POST'])
def create_user():
    if request.method == 'POST':
        datos_recibidos = request.json
        username = datos_recibidos.get('username')
        password = datos_recibidos.get('password')
        name = datos_recibidos.get('name')
        lastname = datos_recibidos.get('lastname')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT `username` FROM `user` WHERE `username` = %s ', (username,))
            rows = cursor.fetchall()
            if len(rows) != 0:
                return jsonify({"mensaje": "Este usuario esta registrado!"})
            
            cursor.execute('INSERT INTO user (username,password,name,lastname) VALUES (%s, %s, %s, %s)', (username,password,name,lastname))
            conn.commit()

            return jsonify({"mensaje": "Usuario añadido exitosamente", "statusCode": 201})
        except Exception as error:
            return jsonify({"mensage":f"No se pudo crear el usuario {error}"})
        finally:
            cursor.close()
            conn.close()
            
            
SECRET_KEY = "asdiuhqafaf+65dg648sedgiu"      
@app.route('/session', methods=['POST'])
def session():
    if request.method == 'POST':
        datos_recibidos = request.json
        username = datos_recibidos.get('username')
        password = datos_recibidos.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM `user` WHERE `username` = %s AND `password` = %s ', (username,password))
            rows = cursor.fetchall()
            print(rows)
            if len(rows) == 0:
                return jsonify({"mensaje": "Sesion NO iniciada exitosamente!", "statusCode": 401})
            payload = {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # El token expirará en 1 hora
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return jsonify({"mensaje": "Sesion iniciada exitosamente!", "token": token, "statusCode": 200, "information": rows })
        except Exception as error:
            return jsonify({"mensage":f"No se pudo iniciar sesion {error}"})
        finally:
            cursor.close()
            conn.close()
    
#funcion para actualizar el estado
def update_status_task(status,id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE `tasks` SET `status` = %s WHERE `id` = %s ', (status,id))
        conn.commit()
        return jsonify({"mensaje": "Task actualizada exitosamente", "statusCode": 200})
    except Exception as error:
        return jsonify({"mensage":f"No se pudo actualizar el estado {error}"})
    finally:
        cursor.close()
        conn.close()


@app.route('/show_task', methods=['POST'])
def manage_users():
    if request.method == 'POST':
        datos_recibidos = request.json
        user_id = datos_recibidos.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM tasks WHERE user_id = %s', (user_id,))
        tasks = cursor.fetchall()

        cursor.execute('SELECT * FROM tasks_resource')
        tasks_resource = cursor.fetchall()
        
        cursor.close()
        conn.close()

        result = {
            'tasks': tasks,
            'tasks_resource': tasks_resource
        }
        
        return jsonify(result)

@app.route('/create_task', methods=['POST'])
def create_task():
    if request.method == 'POST':
        datos_recibidos = request.json
        user_id = datos_recibidos.get('user_id')
        title = datos_recibidos.get('title')
        description = datos_recibidos.get('description')
        resource = datos_recibidos.get('resource')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (user_id,title,description) VALUES (%s, %s, %s)', (user_id,title,description))
            new_id = cursor.lastrowid
            conn.commit()
            
            for res in resource:
                cursor.execute('INSERT INTO tasks_resource (task_id,resource_id) VALUES (%s, %s)', (new_id,res))
                conn.commit()

            return jsonify({"mensaje": "Tarea añadido exitosamente", "statusCode": 201})
        except Exception as error:
            return jsonify({"mensage":f"No se pudo crear la tarea {error}"})
        finally:
            cursor.close()
            conn.close()
            
@app.route('/update_task', methods=['PUT'])
def update_task():
    if request.method == 'PUT':
        datos_recibidos = request.json
        title = datos_recibidos.get('title')
        description = datos_recibidos.get('description')
        id = datos_recibidos.get('id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE `tasks` SET `title` = %s,`description` = %s WHERE `id` = %s ', (title,description,id))
            conn.commit()
            return jsonify({"mensaje": "Task actualizada exitosamente", "statusCode": 200})
        except Exception as error:
            return jsonify({"mensage":f"No se pudo crear el usuario {error}"})
        finally:
            cursor.close()
            conn.close()
            
@app.route('/delete_task', methods=['DELETE'])
def delete_task():
    if request.method == 'DELETE':
        datos_recibidos = request.json
        id = datos_recibidos.get('id')
        return update_status_task(0,id)
    
@app.route('/complete_task', methods=['PUT'])
def complete_task():
    if request.method == 'PUT':
        datos_recibidos = request.json
        id = datos_recibidos.get('id')
        
        return update_status_task(2,id)


if __name__ == '__main__':
    app.run(debug=True, port=4000)