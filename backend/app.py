from flask import Flask, request, jsonify, send_from_directory
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords
import os
import requests

# Tentar carregar variáveis de ambiente do arquivo .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Importar OpenAI SDK para DeepSeek
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False

# Configuração da chave DeepSeek
# IMPORTANTE: Configure a variável de ambiente DEEPSEEK_API_KEY
# Não commite a chave no código!
DEFAULT_DEEPSEEK_KEY = os.getenv('DEEPSEEK_API_KEY')

# Caminho para o frontend (um nível acima)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=FRONTEND_DIR, template_folder=FRONTEND_DIR)

# Baixar stopwords se necessário
try:
    stop_words_pt = stopwords.words("portuguese")
except:
    nltk.download('stopwords')
    stop_words_pt = stopwords.words("portuguese")

# Carregar notícias
NOTICIAS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "noticias.json")
noticias = []
vectorizer = None
tfidf_matrix = None

def carregar_noticias():
    global noticias, vectorizer, tfidf_matrix
    if not noticias:
        with open(NOTICIAS_FILE, encoding="utf-8") as f:
            noticias = json.load(f)
        
        corpus = [
            noticia["titulo"] + " " + noticia["texto"]
            for noticia in noticias
        ]
        
        vectorizer = TfidfVectorizer(stop_words=stop_words_pt, lowercase=True)
        tfidf_matrix = vectorizer.fit_transform(corpus)

def gerar_resposta_ia(pergunta, resultados):
    """Gera uma resposta usando DeepSeek baseada nas notícias encontradas"""
    # Preparar contexto das notícias
    contexto = "\n\n".join([
        f"Título: {r['titulo']}\nTexto: {r['texto'][:500]}"
        for r in resultados[:5]  # Usar top 5 para contexto
    ])
    
    prompt = f"""Com base nas seguintes notícias do IFPE, responda de forma clara e objetiva à pergunta do usuário.

Notícias encontradas:
{contexto}

Pergunta do usuário: {pergunta}

Forneça uma resposta resumida e informativa baseada nas notícias acima. Se as notícias não contiverem informações suficientes, indique isso de forma educada."""
    
    # Chamar DeepSeek
    resposta = chamar_deepseek(prompt)
    if resposta:
        return resposta
    
    # Fallback: resposta básica se DeepSeek falhar
    return formatar_resposta_basica(pergunta, resultados)

def chamar_deepseek(prompt):
    """Chama a API do DeepSeek usando o SDK oficial da OpenAI"""
    api_key = os.getenv('DEEPSEEK_API_KEY') or DEFAULT_DEEPSEEK_KEY
    if not api_key:
        print("⚠️  Aviso: DEEPSEEK_API_KEY não configurada. Configure a variável de ambiente.")
        return None
    
    try:
        # Usar SDK oficial se disponível
        if OPENAI_SDK_AVAILABLE:
            # Criar cliente com a chave atual (pode ter sido alterada via env)
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Você é um assistente que responde perguntas sobre notícias do IFPE de forma clara e objetiva."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                stream=False
            )
            
            return response.choices[0].message.content
        else:
            # Fallback para requisição HTTP direta se SDK não estiver disponível
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Você é um assistente que responde perguntas sobre notícias do IFPE de forma clara e objetiva."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"Erro ao chamar DeepSeek: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao chamar DeepSeek: {e}")
    return None

def formatar_resposta_basica(pergunta, resultados):
    """Formata uma resposta básica quando não há IA disponível"""
    if not resultados:
        return "Não encontrei notícias relacionadas à sua pergunta."
    
    resposta = f"Com base nas notícias encontradas sobre '{pergunta}':\n\n"
    resposta += f"Encontrei {len(resultados)} notícia(s) relevante(s). As principais são:\n\n"
    
    for i, r in enumerate(resultados[:3], 1):
        titulo = r['titulo'][:100] + "..." if len(r['titulo']) > 100 else r['titulo']
        resposta += f"{i}. {titulo}\n"
    
    return resposta

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/buscar', methods=['POST'])
def buscar():
    global noticias, vectorizer, tfidf_matrix
    
    data = request.get_json()
    pergunta = data.get('pergunta', '').strip()
    
    if not pergunta:
        return jsonify({'erro': 'Por favor, digite uma pergunta.'}), 400
    
    try:
        carregar_noticias()
        
        if not vectorizer or tfidf_matrix is None:
            return jsonify({'erro': 'Erro ao carregar o índice TF-IDF.'}), 500
        
        vetor_pergunta = vectorizer.transform([pergunta])
        similaridades = cosine_similarity(vetor_pergunta, tfidf_matrix)[0]
        
        top_k = 10
        indices = np.argsort(similaridades)[::-1][:top_k]
        
        resultados = []
        for i in indices:
            if similaridades[i] > 0:
                resultados.append({
                    'titulo': noticias[i]["titulo"],
                    'url': noticias[i]["url"],
                    'texto': noticias[i]["texto"],
                    'score': float(similaridades[i]),
                    'publicado': noticias[i].get("publicado", "Data não disponível")
                })
        
        # Gerar resposta da IA
        resposta_ia = gerar_resposta_ia(pergunta, resultados)
        
        return jsonify({
            'resposta_ia': resposta_ia,
            'resultados': resultados,
            'total': len(resultados)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao buscar: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)