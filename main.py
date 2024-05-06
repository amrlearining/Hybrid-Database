import base64
from flask import Flask, redirect, render_template, request, url_for
import gridfs
import mysql.connector
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# flask app define
app = Flask(__name__, static_url_path='', static_folder='static')
# data to fetch and deal with mongodb
data = []

# main route
@app.route('/')
def main():
    # connection with relational database
    db = RDB_connection()
    cursor = db.cursor()
    #select The user name
    if cursor:
        cursor.execute("SELECT fname FROM users WHERE id = 1")
        result = cursor.fetchone()
        cursor.close()
    db.close()

    # mongodb connection
    mongodb = MongoDBConnection()
    # fs to uplod and fetch videos
    fs = gridfs.GridFS(mongodb, collection="files")
    videos = []
    files = fs.find()
    for file in files:
        # Read the video file and encode it in Base64
        video_data = file.read()
        video_base64 = base64.b64encode(video_data).decode('utf-8')
        videos.append(video_base64)
    # run index page with information and streaming data    
    return render_template('index.html', re=result[0], videos=videos)

    
# uplod route come from index.html
@app.route('/uplod', methods=['GET', 'POST'])
def uplod():
    # mongodb and sql connections
    db = RDB_connection()
    cursor = db.cursor()
    # users to use it in save method
    if cursor:
        cursor.execute("SELECT fname FROM users")
        name = cursor.fetchall()

    if cursor:
        cursor.execute("SELECT nickname FROM users")
        nick = cursor.fetchall()
        cursor.close()
    db.close()
    # response with uplod.html page
    return render_template('uplod.html', name=name, nick=nick)

# route come from uplod button from uplod.html page
@app.route('/uploadmethod', methods=['POST'])
def uploadmethod():
    #check if there are file
    if 'file' not in request.files:
        return 'No file part'
    # save file data in file 
    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    # fetch data[] from mongodb
    global data
    try:
        mongodb = MongoDBConnection()
    except FileNotFoundError:
        data = []

    # connect to sql
    db = RDB_connection()
    cursor = db.cursor()

    # Save the Video to mongodb
    dataFile = file.read()
    fs = gridfs.GridFS(
        mongodb, 
        collection="files") 
    oid = str(save_data_toMongoDB(dataFile, file.filename, fs))
    # save file name with owner idand object id in sql
    cursor = db.cursor()
    try:
        if cursor:
            nick = request.form['owener'][2:-3]
            cursor.execute("SELECT id FROM users WHERE nickname = %s", (nick,))
            uid = cursor.fetchone()
            if uid:
                user_id = uid[0]
                cursor.execute("INSERT INTO videodata(oid, file_name, owner_id) VALUES(%s, %s, %s)", (oid, file.filename, user_id))
                db.commit()  # Commit the transaction
                cursor.close()
            else:
                print("Owner not found")
    except mysql.connector.Error as err:
        print("MySQL Error: {}".format(err))
    
    # redirect to main 'index.html' page
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

# Mongodb connection
def MongoDBConnection():
    uri = "mongodb+srv://database_user:database_user123@database.x9gzvlv.mongodb.net/?retryWrites=true&w=majority&appName=database"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        collection = client.Hybrid_database.data
        global data
        data = collection.find()
        db = client.Hybrid_database
        return db
    except Exception as e:
        print(e)

def save_data_toMongoDB(dataFile, file_name, fs):
    # put file to mongodb
    return fs.put(dataFile, filename=file_name)

# main method
if __name__ == '__main__':
    app.run(debug=False)