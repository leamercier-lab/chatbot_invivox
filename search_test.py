import os
import json
import numpy as np
from mistralai import Mistral
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "embeddings.csv")

def search(query, top_k=5):
    print("Search asked")
    load_dotenv()
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    # 1. Chargement du CSV (on imagine que la Lambda a inclus name et unique_id dedans)
    if not os.path.exists(CSV_PATH):
        print(f"❌ Erreur : {CSV_PATH} introuvable. Lancez la Lambda d'abord.")
        return []

    df = pd.read_csv(CSV_PATH)

    # 2. Vectorisation de la question
    res = client.embeddings.create(model="mistral-embed", inputs=[query])
    query_vec = np.array(res.data[0].embedding).reshape(1, -1)

    # 3. Calcul de similarité vectorielle (Vectorized operation avec Numpy)
    # On transforme la colonne string 'embedding_vector' en matrice de floats
    # Note : json.loads est nécessaire car le CSV stocke les listes comme du texte
    matrix = np.array([json.loads(v) for v in df['embedding_vector']])

    # Calcul d'un coup sur toute la matrice
    scores = cosine_similarity(query_vec, matrix)[0]
    df['score'] = scores

    # 4. Tri et formatage des résultats
    top_results = df.sort_values(by='score', ascending=False).head(top_k)

    final_results = []
    for _, row in top_results.iterrows():
        final_results.append({
            "id": row.get('training_id') or row.get('id'),
            "name": row['name'],
            "unique_id": row['unique_id'],
            "score": round(row['score'] * 100)
        })

    # Affichage pour tes tests
    print(f"\n🔍 Résultats pour : '{query}'")
    for r in final_results:
        print(f" - [{r['score']}%] {r['name']} (ID: {r['unique_id']})")

    return final_results
