import os
from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory 

load_dotenv()
factory = StemmerFactory()
stemmer = factory.create_stemmer()

app = Flask(__name__)

client = MongoClient(os.environ.get('MONGO_DB'))
db = client[os.environ.get('MONGO_DB_DATABASE')]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/retrieve', methods=['POST'])
def retrieve():
    collection = db[os.environ.get('MONGO_DB_COLLECTION')]

    query = {}
    projection = {'_id': 0,'isiDocx': 1}
    projection2 = {'_id': 0,'class': 1}
    
    documentx = collection.find(query, projection)
    classx = collection.find(query, projection2)
    
    text = [str(document['isiDocx']) for document in documentx]
    label = [str(document['class']) for document in classx]
    
    search_query = request.form['search']

    documents = text
    documents.append(search_query)
    
    documents = [doc.lower() for doc in documents] # Case Folding
    documents = [stemmer.stem(teks) for teks in documents] # Stemming
    # Inisialisasi objek TfidfVectorizer dengan smooth_idf=False
    vectorizer = TfidfVectorizer(smooth_idf=False)

    # Proses teks menggunakan fit_transform
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Hitung kemiripan vektor dokumen
    similarity_matrix = cosine_similarity(tfidf_matrix)

    document_index = len(documents)-1  # Indeks Query

    # Melakukan prediksi label Dokumen 5 menggunakan k-NN
    k = 3  # Jumlah tetangga terdekat yang akan digunakan dalam prediksi
    neighbors_indices = similarity_matrix[document_index].argsort()[-k-1:-1]

    predicted_labels = [label[i] for i in neighbors_indices]

    # Menampilkan prediksi label Dokumen 5
    predicted_label = max(set(predicted_labels), key=predicted_labels.count)

    queryx = {'class': predicted_label}
    projectiony = {'_id': 0, 'dokumen': 1, 'isiDocx': 1, 'class': 1 }
    documenty = collection.find(queryx, projectiony)

    return render_template('retrieve.html', strings=predicted_label, search_query=search_query,   documenty=documenty)

if __name__ == "__main__":
    app.run(debug=True)