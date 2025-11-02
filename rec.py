import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

def extrair_informacoes(url):
    resposta = requests.get(url)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, 'lxml')

    # Extrai título
    titulo = soup.find('h1') or soup.find('title')
    titulo = titulo.get_text(strip=True) if titulo else "Sem título"

    # Extrai data de publicação
    publicado = soup.find('span', class_='documentPublished')
    if not publicado:
        publicado = soup.find(string=lambda s: s and "Publicado" in s)
    publicado = publicado.get_text(strip=True) if hasattr(publicado, 'get_text') else (publicado or "Data de publicação não encontrada")

    # Extrai data de modificação
    modificado = soup.find('span', class_='documentModified')
    if not modificado:
        modificado = soup.find(string=lambda s: s and "última modificação" in s.lower())
    modificado = modificado.get_text(strip=True) if hasattr(modificado, 'get_text') else (modificado or "Data de modificação não encontrada")

    # Extrai corpo
    corpo = soup.find('div', class_='documentDescription') or \
            soup.find('div', class_='content-core') or \
            soup.find('article')

    if corpo:
        texto = ' '.join(p.get_text(strip=True) for p in corpo.find_all('p'))
    else:
        texto = "Conteúdo não encontrado"

    # Extrai links relacionados
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True) if 'ifpe.edu.br' in a['href']]

    return {
        'url': url,
        'titulo': titulo,
        'publicado': publicado,
        'modificado': modificado,
        'texto': texto[:800] + '...' if len(texto) > 800 else texto,
        'links_relacionados': links
    }


if __name__ == "__main__":
    # Permite passar a URL pelo terminal
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://portal.ifpe.edu.br/noticias/divulgado-resultado-final-das-candidaturas-a-cppd/"

    info = extrair_informacoes(url)

    console.rule("[bold green]🔍 INFORMAÇÕES EXTRAÍDAS DO IFPE")

    console.print(Panel(Text(info['titulo'], justify="center", style="bold yellow"), title="📰 TÍTULO"))

    console.print(f"[bold cyan]📅 Publicado:[/bold cyan] {info['publicado']}")
    console.print(f"[bold cyan]🕓 Última modificação:[/bold cyan] {info['modificado']}")
    console.print(f"[bold cyan]🔗 URL:[/bold cyan] {info['url']}\n")

    console.print(Panel(info['texto'], title="📄 CONTEÚDO (Resumo)", subtitle="(até 800 caracteres)", expand=False))

    if info['links_relacionados']:
        tabela = Table(title="🔗 LINKS RELACIONADOS", show_header=True, header_style="bold magenta")
        tabela.add_column("Nº", justify="right")
        tabela.add_column("Link")
        for i, link in enumerate(info['links_relacionados'][:10], start=1):
            tabela.add_row(str(i), link)
        console.print(tabela)
    else:
        console.print("[yellow]Nenhum link relacionado encontrado.[/yellow]")

    console.rule("[green]✅ Fim da extração")
