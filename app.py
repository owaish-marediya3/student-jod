import os
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
import psycopg2
from psycopg2 import errors
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

# Threaded connection pool for maximum speed and concurrent requests
db_pool = None

def get_pool():
    global db_pool
    if db_pool is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is missing. Please set it in your .env file.")
        db_pool = ThreadedConnectionPool(1, 20, dsn=DATABASE_URL)
    return db_pool

def connection():
    return get_pool().getconn()

def put_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)

def fetchRecord():
    con = connection()
    cursor = con.cursor()
    try:
        cursor.execute('SELECT id, name, phonenumber, qualification FROM studentjod')
        data = cursor.fetchall()
        return data
    finally:
        cursor.close()
        put_connection(con)

def createuser(data):
    conn = connection()
    cur = conn.cursor()
    try:
        sql_query = 'INSERT INTO studentjod (name, phonenumber, qualification) VALUES (%s, %s, %s)'
        cur.execute(sql_query, (data['name'], data['phonenumber'], data['qualification']))
        conn.commit()
        return "success"
    except errors.UniqueViolation:
        conn.rollback()
        return "exists"
    except Exception as e:
        conn.rollback()
        return "error"
    finally:
        cur.close()
        put_connection(conn)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    result = createuser(data)
    
    if result == "success":
        return jsonify({"status": "success", "redirect": url_for('success_page')}), 200
    elif result == "exists":
        return jsonify({"error": "user already exists"}), 409
    else:
        return jsonify({"error": "server error"}), 500

@app.route('/success')
def success_page():
    return render_template('redirect.html')

@app.route('/admin')
def showAdmin():
    return render_template('admin.html')

@app.route('/authAdmin', methods=['POST'])
def Auth():
    realusername = os.getenv('ADMIN_USERNAME', '@Owaish')
    realpassword = os.getenv('ADMIN_PASSWORD', '@Owaish10')
    
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        
    if username == realusername and password == realpassword:
        return jsonify({"status": "success", "html": render_template('dashboard.html')}), 200
        
    return jsonify({"status": "error", "error": "Wrong username and password"}), 401

@app.route('/fetch-data')
def fetchdata():
    return jsonify(fetchRecord())

@app.route('/check-phone')
def check_phone():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({"error": "phone parameter required"}), 400
        
    con = connection()
    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM studentjod WHERE phonenumber = %s', (phone,))
        exists = cursor.fetchone() is not None
        return jsonify({"exists": exists}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        put_connection(con)

@app.route('/delete-student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    con = connection()
    cursor = con.cursor()
    try:
        cursor.execute('DELETE FROM studentjod WHERE id = %s', (student_id,))
        con.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        con.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        put_connection(con)

if __name__ == '__main__':
    app.run(debug=True)