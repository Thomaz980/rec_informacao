document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const clearButton = document.getElementById('clearButton');
    const resultsWrapper = document.getElementById('resultsWrapper');
    const resultsList = document.getElementById('resultsList');
    const resultsInfo = document.getElementById('resultsInfo');
    const aiContent = document.getElementById('aiContent');

    function performSearch() {
        const query = searchInput.value.trim();
        
        if (!query) {
            return;
        }

        // Mostrar loading
        resultsWrapper.style.display = 'block';
        aiContent.textContent = 'Gerando resposta...';
        resultsList.innerHTML = '<div class="no-results"><p>Buscando...</p></div>';
        resultsInfo.textContent = '';

        // Fazer requisição
        fetch('/buscar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pergunta: query })
        })
        .then(response => response.json())
        .then(data => {
            if (data.erro) {
                aiContent.textContent = `Erro: ${data.erro}`;
                resultsList.innerHTML = `<div class="no-results"><h2>Erro</h2><p>${data.erro}</p></div>`;
                resultsInfo.textContent = '';
                return;
            }

            if (!data.resultados || data.resultados.length === 0) {
                aiContent.textContent = 'Não encontrei notícias relacionadas à sua pergunta. Tente usar outras palavras-chave.';
                resultsList.innerHTML = '<div class="no-results"><h2>Nenhum resultado encontrado</h2><p>Tente usar outras palavras-chave.</p></div>';
                resultsInfo.textContent = '';
                return;
            }

            // Mostrar resposta da IA
            if (data.resposta_ia) {
                aiContent.textContent = data.resposta_ia;
            } else {
                aiContent.textContent = 'Resposta não disponível.';
            }

            // Mostrar informações
            resultsInfo.textContent = `${data.total} resultado(s)`;

            // Renderizar resultados (apenas links no lado direito)
            resultsList.innerHTML = data.resultados.map((result, index) => {
                const scorePercent = (result.score * 100).toFixed(1);
                
                return `
                    <div class="result-item">
                        <h3 class="result-title">
                            <a href="${result.url}" target="_blank">${escapeHtml(result.titulo)}</a>
                        </h3>
                        <div class="result-url">
                            <a href="${result.url}" target="_blank">${extractDomain(result.url)}</a>
                        </div>
                        <div class="result-meta">
                            <span class="result-date">${result.publicado}</span>
                            <span>•</span>
                            <span>Relevância: ${scorePercent}%</span>
                        </div>
                    </div>
                `;
            }).join('');
        })
        .catch(error => {
            console.error('Erro:', error);
            aiContent.textContent = 'Erro ao gerar resposta. Tente novamente mais tarde.';
            resultsList.innerHTML = '<div class="no-results"><h2>Erro ao buscar</h2><p>Tente novamente mais tarde.</p></div>';
            resultsInfo.textContent = '';
        });
    }

    function extractDomain(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.hostname.replace('www.', '');
        } catch {
            return url;
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Função para mostrar/esconder botão de limpar
    function toggleClearButton() {
        if (searchInput.value.trim() !== '') {
            clearButton.classList.remove('hidden');
        } else {
            clearButton.classList.add('hidden');
        }
    }

    // Função para limpar busca
    function clearSearch() {
        searchInput.value = '';
        clearButton.classList.add('hidden');
        resultsWrapper.style.display = 'none';
        searchInput.focus();
    }

    // Event listeners
    searchButton.addEventListener('click', performSearch);
    
    clearButton.addEventListener('click', clearSearch);
    
    searchInput.addEventListener('input', toggleClearButton);
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Focar no input ao carregar
    searchInput.focus();
    toggleClearButton();
});

