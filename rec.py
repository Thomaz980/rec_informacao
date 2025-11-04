import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

def limpar_texto(texto):
    """Remove caracteres especiais e espaços extras."""
    if not texto:
        return ""
    return (
        texto.replace('\xa0', ' ')
        .replace('&nbsp;', ' ')
        .replace('>>>', '')
        .strip()
    )

def extrair_informacoes(url):
    resposta = requests.get(url)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, 'lxml')

    titulo = soup.find('h1') or soup.find('title')
    titulo = titulo.get_text(strip=True) if titulo else "Sem título"

    publicado = soup.find('span', class_='post__published')
    if not publicado:
        publicado = soup.find(string=lambda s: s and "Publicado" in s)
    publicado = publicado.get_text(strip=True) if hasattr(publicado, 'get_text') else (publicado or "Data de publicação não encontrada")

    modificado = soup.find('span', class_='post__updated')
    if not modificado:
        modificado = soup.find(string=lambda s: s and "última modificação" in s.lower())
    modificado = modificado.get_text(strip=True) if hasattr(modificado, 'get_text') else (modificado or "Data de modificação não encontrada")

    corpo = soup.find('div', class_='post__content')
    
    if corpo and corpo.find('p'):
        texto = corpo.find('p').get_text(strip=True)
    else:
        texto = "Conteúdo não encontrado"

    links_especificos = []
    links_gerais = []

    for a in soup.find_all('a', href=True):
        href = urljoin(url, a['href'])
        if not href.startswith("http"):
            continue

        texto_link = a.get_text(" ", strip=True)
        if not texto_link:
            continue

        texto_limpo = limpar_texto(texto_link)
        if len(texto_limpo) < 3:
            continue

        dentro_do_texto = a.find_parent('p') or a.find_parent('strong')

        if dentro_do_texto:
            links_especificos.append({
                'texto': texto_limpo,
                'url': href
            })
        else:
            links_gerais.append({
                'texto': texto_limpo,
                'url': href
            })

    return {
        'url': url,
        'titulo': titulo,
        'publicado': publicado,
        'modificado': modificado,
        'texto': texto[:800] + '...' if len(texto) > 800 else texto,
        'links_especificos': links_especificos,
        'links_gerais': links_gerais
    }

if __name__ == "__main__":
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

    if info['links_especificos']:
        tabela = Table(title="🎯 LINKS ESPECÍFICOS (no texto da notícia)", show_header=True, header_style="bold green")
        tabela.add_column("Nº", justify="right")
        tabela.add_column("Texto")
        tabela.add_column("URL")
        for i, link in enumerate(info['links_especificos'], start=1):
            tabela.add_row(str(i), link['texto'], link['url'])
        console.print(tabela)
    else:
        console.print("[yellow]Nenhum link específico encontrado no corpo da notícia.[/yellow]")

    if info['links_gerais']:
        tabela = Table(title="🔗 LINKS GERAIS DO PORTAL", show_header=True, header_style="bold magenta")
        tabela.add_column("Nº", justify="right")
        tabela.add_column("Texto")
        tabela.add_column("URL")
        for i, link in enumerate(info['links_gerais'][:10], start=1):
            tabela.add_row(str(i), link['texto'], link['url'])
        console.print(tabela)
    else:
        console.print("[yellow]Nenhum link geral encontrado.[/yellow]")

    console.rule("[green]✅ Fim da extração")
