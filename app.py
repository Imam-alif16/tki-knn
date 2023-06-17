from flask import Flask, render_template, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['tki']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/retrieve')
def retrieve():
    collection = db['test']

    documents = collection.find()

    return render_template('retrieve.html', documents=documents)

@app.route('/admin')
def admin():
    return redirect(url_for('user', name='Vallianz!'))

if __name__ == "__main__":
    app.run(debug=True)