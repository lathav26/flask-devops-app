import os
import time
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'mysql')  # IMPORTANT: use 'mysql'
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'root')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'mydatabase')

# Initialize MySQL
mysql = MySQL(app)

# ✅ FIXED: Retry logic for DB connection
def init_db():
    with app.app_context():
        for i in range(10):  # try 10 times
            try:
                cur = mysql.connection.cursor()
                cur.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT
                );
                ''')
                mysql.connection.commit()
                cur.close()
                print("✅ Database connected successfully")
                break
            except Exception as e:
                print("❌ Database not ready, retrying...")
                time.sleep(3)

# Home route
@app.route('/')
def hello():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT message FROM messages')
        messages = cur.fetchall()
        cur.close()
    except:
        messages = []
    return render_template('index.html', messages=messages)

# Submit route
@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    try:
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print("Insert error:", e)
    return jsonify({'message': new_message})

# Run app
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)