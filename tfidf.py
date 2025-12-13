import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import sys

if len(sys.argv) < 2:
    print("Uso: python3 tfidf <pergunta entre aspas>")
    sys.exit(1)

# Baixar stopwords em português do NLTK
nltk.download('stopwords')
from nltk.corpus import stopwords

# Carregar stopwords em português
stop_words_pt = stopwords.words("portuguese")

# 1. Carregar as notícias do arquivo JSON
with open("noticias.json", encoding="utf-8") as f:
    noticias = json.load(f)

# 2. Criar o corpus (texto das notícias)
corpus = [
    noticia["titulo"] + " " + noticia["texto"]  # Título + Texto da notícia
    for noticia in noticias
]

# 3. Criar o vetor TF-IDF
vectorizer = TfidfVectorizer(stop_words=stop_words_pt, lowercase=True)

tfidf_matrix = vectorizer.fit_transform(corpus)

# 4. Receber a pergunta do usuário
pergunta = sys.argv[1]
# pergunta = "quando abrem inscricoes para o processo seletivo"

# 5. Transformar a pergunta no mesmo espaço vetorial
vetor_pergunta = vectorizer.transform([pergunta])

# 6. Calcular a similaridade entre a pergunta e as notícias
similaridades = cosine_similarity(vetor_pergunta, tfidf_matrix)[0]

# 7. Ordenar as notícias pela similaridade (do mais relevante para o menos)
top_k = 3  # Pode ser ajustado conforme necessário
indices = np.argsort(similaridades)[::-1][:top_k]


print("Pergunta:", pergunta)
# 8. Exibir os resultados
for i in indices:
    print("\nTítulo:", noticias[i]["titulo"])
    print("URL:", noticias[i]["url"])
    print("Score de Similaridade:", round(similaridades[i], 3))
    print("Trecho:", noticias[i]["texto"][:300], "...")  # Exibindo um resumo
