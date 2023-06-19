import os
from flask import Flask, render_template, request
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
    
    def KNN_Model(documents, k=3):
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
        return predicted_label
    
    predicted_label = KNN_Model(documents, k=3)

    queryx = {'class': predicted_label}
    projectiony = {'_id': 0, 'dokumen': 1, 'isiDocx': 1, 'class': 1 }
    documenty = collection.find(queryx, projectiony)

    def cosine_similarity_search(query, documents):
        # Menginisialisasi vektorizer TF-IDF
        vectorizer = TfidfVectorizer(smooth_idf=False)
        
        # Mengubah dokumen menjadi matriks TF-IDF
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Mengubah query menjadi vektor TF-IDF
        query_vector = vectorizer.transform([query])
        
        # Menghitung similarity antara vektor query dan dokumen menggunakan cosine similarity
        similarities = cosine_similarity(query_vector, tfidf_matrix)
        
        # Mengurutkan dokumen berdasarkan similarity tertinggi
        sorted_indices = similarities.argsort()[0][::-1]
        
        # Mendapatkan dokumen terurut berdasarkan indeks beserta nilai cosine similarity
        results = [documents[index] for index in sorted_indices if index != len(documents) - 1 and similarities[0][index] > 0]
        
        return results

    query = documents[len(documents)-1 ]
    results_xzy = cosine_similarity_search(query, documents)

    queryxz = { 'isiDocx': { '$in': results_xzy } }
    resultxz = collection.find(queryxz)

    yakult = []
    for result in resultxz:
        index = results_xzy.index(result['isiDocx'])
        yakult.insert(index, result)

    return render_template('retrieve.html', strings=predicted_label, search_query=search_query, documenty=documenty, dokumenz = yakult)

if __name__ == "__main__":
    app.run(debug=True)