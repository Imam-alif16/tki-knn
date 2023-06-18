import os
from flask import Flask, render_template, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    projection2 = {'_id': 0,'class': 1}
    
    documentx = collection.find(query, projection)
    classx = collection.find(query, projection2)
    
    text = [str(document['isiDocx']) for document in documentx]
    label = [str(document['class']) for document in classx]
    
    documents = text
    print(documents)
    documents.append("tanding sepakbola persebaya kampanye pemilu 2009 tunda")
    print(documents)
    # # Inisialisasi objek TfidfVectorizer dengan smooth_idf=False
    vectorizer = TfidfVectorizer(smooth_idf=False)

    # # Proses teks menggunakan fit_transform
    tfidf_matrix = vectorizer.fit_transform(documents)

    # # Hitung kemiripan vektor dokumen
    similarity_matrix = cosine_similarity(tfidf_matrix)

    document_index = len(documents)-1  # Indeks Dokumen 5 dalam daftar dokumen (indeks dimulai dari 0)

    # Melakukan prediksi label Dokumen 5 menggunakan k-NN
    k = 3  # Jumlah tetangga terdekat yang akan digunakan dalam prediksi
    neighbors_indices = similarity_matrix[document_index].argsort()[-k-1:-1]

    predicted_labels = [label[i] for i in neighbors_indices]

    # Menampilkan prediksi label Dokumen 5
    predicted_label = max(set(predicted_labels), key=predicted_labels.count)

    return render_template('retrieve.html', strings=predicted_label)

@app.route('/admin')
def admin():
    return redirect(url_for('user', name='Vallianz!'))

if __name__ == "__main__":
    app.run(debug=True)