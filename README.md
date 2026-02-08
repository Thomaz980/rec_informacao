# 🔍 Sistema de Busca de Notícias IFPE Igarassu

Sistema de recuperação de informação que busca e ranqueia notícias do IFPE usando TF-IDF (Term Frequency-Inverse Document Frequency) e Similaridade de Cosseno.

## 📋 Descrição

Este projeto implementa um sistema de busca de notícias com interface web estilo Google, permitindo que usuários pesquisem e encontrem notícias relevantes do portal IFPE de forma rápida e eficiente.

### Funcionalidades

- ✅ **Interface Web** estilo Google com logo IFPE
- ✅ **Resumo gerado por IA** (DeepSeek) no lado esquerdo
- ✅ **Busca por relevância** usando TF-IDF
- ✅ **Ranqueamento** por similaridade de cosseno
- ✅ **Resultados organizados** com título, URL e porcentagem de relevância
- ✅ **Design responsivo** para desktop e mobile

## 🚀 Tecnologias Utilizadas

- **Python 3.x**
- **Flask** - Framework web para criar a API
- **scikit-learn** - Implementação de TF-IDF e similaridade de cosseno
- **NLTK** - Processamento de linguagem natural e stopwords em português
- **NumPy** - Operações matemáticas e manipulação de arrays
- **OpenAI SDK** - Integração com DeepSeek para geração de resumos
- **HTML/CSS/JavaScript** - Interface frontend

## 📁 Estrutura do Projeto

```
rec_informacao/
│
├── backend/
│   ├── app.py             # Backend Flask (API e integração TF-IDF)
│   ├── rec.py             # Script para coletar notícias do portal IFPE
│   └── tfidf.py           # Script para busca TF-IDF
|
├── frontend/
│   ├── index.html         # Interface web principal
│   ├── style.css          # Estilos CSS (estilo Google)
│   └── script.js          # JavaScript para busca e exibição de resultados
│
├── noticias.json          # Base de dados de notícias (JSON)
├── requirements.txt       # Dependências do projeto
└── README.md

```

## 🛠️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/Thomaz980/rec_informacao.git
cd rec_informacao
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Baixe os recursos do NLTK

O sistema faz isso automaticamente na primeira execução, mas você pode fazer manualmente:

```python
import nltk
nltk.download('stopwords')
```

### 4. Configure a chave de API da IA (Opcional)

O sistema usa **DeepSeek** por padrão para gerar resumos das notícias. A chave já está configurada no código, mas você pode configurar sua própria chave:

**Opção 1: Usar a chave já configurada (recomendado)**
- A chave já está no código, então não precisa fazer nada!

**Opção 2: Configurar sua própria chave**

No Windows (PowerShell):
```powershell
$env:DEEPSEEK_API_KEY="sua_chave_aqui"
```

No Linux/Mac:
```bash
export DEEPSEEK_API_KEY=sua_chave_aqui
```

**Para obter uma chave:**
1. Acesse: https://platform.deepseek.com/api_keys
2. Faça login ou crie uma conta
3. Clique em "Create API Key"
4. Copie a chave gerada

> **Nota:** Se não configurar uma chave, o sistema ainda funciona, mas mostrará uma resposta básica ao invés de um resumo gerado por IA.

## 📊 Como Usar

> **Importante:** Certifique-se de ter o arquivo `noticias.json` na raiz do projeto. Se não tiver, execute primeiro `python backend/rec.py` para coletar as notícias.

1. **Inicie o servidor Flask:**

```bash
cd backend
python app.py
```

2. **Acesse no navegador:**

```
http://127.0.0.1:5000
```

3. **Faça uma busca:**

   - Digite sua pergunta na barra de pesquisa
   - Clique no ícone de busca ou pressione Enter
   - Visualize os resultados ranqueados por relevância

### Coletar Novas Notícias

Para atualizar a base de notícias (`noticias.json`):

```bash
python backend/rec.py
```

Ou, se estiver na raiz do projeto:

```bash
python backend/rec.py
```

Este script faz web scraping do portal IFPE e gera o arquivo `noticias.json` com todas as notícias coletadas.

## 🔬 Metodologia

### 1. Coleta de Dados

- O script `rec.py` faz web scraping do portal IFPE
- Extrai: título, texto, data de publicação e URL de cada notícia
- Salva os dados em `noticias.json`

### 2. Processamento e Indexação

- **Pré-processamento:**
  - Remoção de stopwords em português
  - Conversão para lowercase
  - Combinação de título + texto para cada documento

- **TF-IDF:**
  - Cria a matriz termo-documento
  - Calcula a importância de cada termo em cada documento
  - Normaliza os pesos para evitar viés por tamanho do documento

### 3. Busca e Ranqueamento

- **Vetorização da Query:**
  - Transforma a pergunta do usuário no mesmo espaço vetorial do TF-IDF

- **Similaridade de Cosseno:**
  - Calcula o ângulo entre o vetor da query e cada documento
  - Retorna score entre 0 (sem similaridade) e 1 (idêntico)

- **Ranqueamento:**
  - Ordena documentos por score decrescente
  - Retorna top-10 mais relevantes
  - Filtra resultados com score > 0

## 📈 Exemplo de Resultados

**Query:** "processo seletivo 2026"

```
Título: IFPE lança Processo de Ingresso para o semestre 2026.1
URL: https://portal.ifpe.edu.br/noticias/...
Score: 0.856 (85.6% de relevância)
Snippet: O Instituto Federal de Pernambuco (IFPE) divulgou...
```

## 🎨 Interface Web

- ✅ Layout estilo Google
- ✅ Logo IFPE no topo
- ✅ Barra de pesquisa centralizada
- ✅ **Resumo gerado por IA** no lado esquerdo (usando DeepSeek)
- ✅ **Links para notícias** no lado direito com scroll independente
- ✅ Resultados organizados com:
  - Título clicável
  - URL do site
  - Data de publicação
  - Porcentagem de relevância
- ✅ Design responsivo (mobile-friendly)

## ⚙️ Configurações

### Ajustar número de resultados

No arquivo `app.py`, linha 58:

```python
top_k = 10  # Altere para o número desejado
```

### Ajustar número de páginas coletadas

No arquivo `rec.py`, linha 158:

```python
total_paginas = 20  # Altere para coletar mais ou menos páginas
```

## 🔧 Requisitos do Sistema

- Python 3.7 ou superior
- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Conexão com internet (para coletar notícias)

## 📝 Notas

- O arquivo `noticias.json` deve existir antes de executar a busca
- A primeira execução pode demorar um pouco para baixar os recursos do NLTK
- Os resultados são baseados na similaridade textual, não em busca semântica avançada


## 📄 Licença
Este projeto é de código aberto para fins educacionais.

## 👨‍💻 Autores
**Andrey Mafra** - [@andreymafra55](https://github.com/andreymafra55)

**Caio Rodrigues** - [@caiordm](https://github.com/caiordm)

**Polyana Gisele** - [@Polyalves2](https://github.com/Polyalves2)

**Thomaz Rodrigues** - [@Thomaz980](https://github.com/Thomaz980)

**Victor Antônio** - [@VictorLemos1000](https://github.com/VictorLemos1000)

**Williane Felix** - [@willyfelix](https://github.com/willyfelix)

---
**Projeto desenvolvido para a disciplina de Recuperação de Informação**

