import os
from flask import Flask, render_template, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.environ.get('MONGO_DB'))
db = client[os.environ.get('MONGO_DB_DATABASE')]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/retrieve')
def retrieve():
    collection = db[os.environ.get('MONGO_DB_COLLECTION')]

    query = {}
    projection = {'_id': 0,'isiDocx': 1}

    documents = collection.find(query, projection)

    strings = [str(document['isiDocx']) for document in documents]
    print(strings)

    return render_template('retrieve.html', strings=strings)

@app.route('/admin')
def admin():
    return redirect(url_for('user', name='Vallianz!'))

if __name__ == "__main__":
    app.run(debug=True)