import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import sys

if len(sys.argv) < 2:
    print("Uso: python3 tfidf <pergunta entre aspas>")
    sys.exit(1)


nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words_pt = stopwords.words("portuguese")

with open("noticias.json", encoding="utf-8") as f:
    noticias = json.load(f)

corpus = [
    noticia["titulo"] + " " + noticia["texto"]  # Título + Texto da notícia
    for noticia in noticias
]

# 3. Criar o vetor TF-IDF
vectorizer = TfidfVectorizer(stop_words=stop_words_pt, lowercase=True)

tfidf_matrix = vectorizer.fit_transform(corpus)

pergunta = sys.argv[1]
# pergunta = "quando abrem inscricoes para o processo seletivo"

vetor_pergunta = vectorizer.transform([pergunta])

similaridades = cosine_similarity(vetor_pergunta, tfidf_matrix)[0]

# Ordenar as notícias pela similaridade (do mais relevante para o menos)
top_k = 5
indices = np.argsort(similaridades)[::-1][:top_k]


print("Pergunta:", pergunta)
# 8. Exibir os resultados
for i in indices:
    print("\nTítulo:", noticias[i]["titulo"])
    print("URL:", noticias[i]["url"])
    print("Score de Similaridade:", round(similaridades[i], 3))
    print("Trecho:", noticias[i]["texto"][:300], "...")  # Exibindo um resumo
