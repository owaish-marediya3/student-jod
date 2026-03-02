from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
import psycopg2
from psycopg2 import errors

app = Flask(__name__)

DBdetails = {
    'host': 'aws-1-ap-southeast-1.pooler.supabase.com',
    'port': 5432,
    'database': 'postgres',
    'password': '@Noorani3131',
    'user': 'postgres.jnfjpipqwcsrsefqfckj'
}

def connection():
    return psycopg2.connect(**DBdetails)

def fetchRecord():
    con = connection()
    cursor = con.cursor()
    cursor.execute('SELECT id, name, phonenumber, qualification FROM studentjod')
    data = cursor.fetchall()
    cursor.close()
    con.close()
    return data

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
        conn.close()

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
    realusername = '@Owaish'
    realpassword = '@Owaish10'
    username = request.form.get('username')
    password = request.form.get('password')
    if username == realusername and password == realpassword:
        return render_template('dashboard.html')
    return "Wrong username and password"

@app.route('/fetch-data')
def fetchdata():
    return jsonify(fetchRecord())


if __name__ == '__main__':
    app.run(debug=True)