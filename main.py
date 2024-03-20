import os
from flask import Flask, redirect, render_template, request, url_for
import json
import mysql.connector

app = Flask(__name__, static_url_path='', static_folder='static')

data = []

# Routes
@app.route('/')
def main():
    nosqlDB_connection()
    db = RDB_connection()
    cursor = db.cursor()
    
    if cursor:
        cursor.execute("SELECT fname FROM users WHERE id = 1")
        result = cursor.fetchone()
        print(result)
        cursor.close()
    
    db.close()
    return render_template('index.html', re=result[0], vid=data)

@app.route('/uplod', methods=['GET', 'POST'])
def uplod():
    nosqlDB_connection()
    db = RDB_connection()
    cursor = db.cursor()
    
    if cursor:
        cursor.execute("SELECT fname FROM users")
        name = cursor.fetchall()

    if cursor:
        cursor.execute("SELECT nickname FROM users")
        nick = cursor.fetchall()
        cursor.close()
    
    db.close()
    return render_template('uplod.html', name=name, nick=nick)

@app.route('/uploadmethod', methods=['POST'])
def uploadmethod():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    upload_folder = 'static/'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # data id
    global data
    try:
        with open('nosql.json', 'r') as jfile:
            data = json.load(jfile)
    except FileNotFoundError:
        data = []

    last_item = data[-1]
    id = int(last_item['id']) + 1

    # owner id
    db = RDB_connection()
    cursor = db.cursor()

    if cursor:
        cursor.execute("SELECT id FROM users WHERE nickname = %s", (request.form['owener'],))
        oid = cursor.fetchone()
        cursor.close()
    
    # Save the file name to a JSON file
    data.append({"id": id, "source": file.filename, "owner_id": oid[0]})

    json_file_path = 'nosql.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)

    return redirect(url_for('main'))


# Connect to the relational database
def RDB_connection():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="proj"
        )
        return mydb
    except mysql.connector.Error as error:
        print("Error connecting to the database:", error)
        return None

# Other methods
def nosqlDB_connection():
    global data
    try:
        with open('nosql.json', 'r') as jfile:
            data = json.load(jfile)
    except FileNotFoundError:
        data = []

def save_data_tonosqlDB():
    with open('nosql.json', 'w') as jfile:
        json.dump(data, jfile, indent=4)


if __name__ == '__main__':
    app.run(debug=True)