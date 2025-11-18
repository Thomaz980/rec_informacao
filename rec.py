import sys
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def limpar_texto(texto):
    if not texto:
        return ""
    return (
        texto.replace('\xa0', ' ')
        .replace('&nbsp;', ' ')
        .replace('>>>', '')
        .strip()
    )


def eh_noticia_valida(url):
    if url.endswith("/noticias/"):
        return False
    if "/categoria/" in url:
        return False
    if "/tag/" in url:
        return False
    if "/o-ifpe/" in url and "/noticias/" not in url:
        return False
    if "/noticias/" in url and url.count("/") >= 5:
        return True
    return False


def extrair_informacoes(url):
    resposta = requests.get(url)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, 'lxml')

    titulo = None

    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        titulo = og["content"].strip()

    if not titulo:
        h1 = soup.find("h1", class_="post__title")
        if h1:
            titulo = h1.get_text(strip=True)

    if not titulo:
        h1_old = soup.find("h1", class_="documentFirstHeading")
        if h1_old:
            titulo = h1_old.get_text(strip=True)

    if not titulo:
        titulo = soup.find("title").get_text(strip=True) if soup.find("title") else "Sem título"


    publicado = soup.find("span", class_="post__published")
    if not publicado:
        publicado = soup.find(string=lambda s: s and "publicado" in s.lower())

    publicado = publicado.get_text(strip=True) if hasattr(publicado, "get_text") else "Data não encontrada"

    modificado = soup.find("span", class_="post__updated")
    if not modificado:
        modificado = soup.find(string=lambda s: s and "modifica" in s.lower())

    modificado = modificado.get_text(strip=True) if hasattr(modificado, "get_text") else "Data não encontrada"


    corpo = soup.find('div', class_='post__content')
    if corpo and corpo.find('p'):
        texto = corpo.find('p').get_text(strip=True)
    else:
        p = soup.find("p")
        texto = p.get_text(strip=True) if p else "Conteúdo não encontrado"

   
    links_especificos = []
    links_gerais = []

    for a in soup.find_all('a', href=True):
        href = urljoin(url, a['href'])
        texto_link = limpar_texto(a.get_text(" ", strip=True))
        if len(texto_link) < 3:
            continue

        if a.find_parent('p') or a.find_parent('strong'):
            links_especificos.append({"texto": texto_link, "url": href})
        else:
            links_gerais.append({"texto": texto_link, "url": href})

    return {
        "url": url,
        "titulo": titulo,
        "publicado": publicado,
        "modificado": modificado,
        "texto": texto[:800] + "..." if len(texto) > 800 else texto,
        "links_especificos": links_especificos,
        "links_gerais": links_gerais
    }


def listar_links_de_noticias(url):
    resposta = requests.get(url)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, 'lxml')
    links = []

    for a in soup.find_all('a', href=True):
        href = urljoin(url, a['href'])
        if eh_noticia_valida(href):
            links.append(href)

    return list(dict.fromkeys(links))  # remove duplicados


def gerar_urls_paginas(base_url, total_paginas):
    return [f"{base_url}?b_start:int={pagina * 15}" for pagina in range(total_paginas)]


if __name__ == "__main__":

    base = "https://portal.ifpe.edu.br/noticias"
    total_paginas = 5

    paginas = gerar_urls_paginas(base, total_paginas)
    todas_noticias = []

    for pagina in paginas:
        console.rule(f"[bold green]📄 Lendo página: {pagina}")

        noticias = listar_links_de_noticias(pagina)

        if not noticias:
            console.print("[yellow]Nenhuma notícia encontrada nessa página.[/yellow]")
            continue

        for link in noticias:
            console.rule(f"[bold cyan]🔗 Notícia: {link}")

            try:
                info = extrair_informacoes(link)
            except Exception as e:
                console.print(f"[red]Erro ao ler notícia: {e}[/red]")
                continue

            todas_noticias.append(info)

            console.print(Panel(
                Text(info['titulo'], justify="center", style="bold yellow"),
                title="📰 TÍTULO"
            ))
            console.print(f"[cyan]Publicado:[/cyan] {info['publicado']}")
            console.print(f"[cyan]Modificado:[/cyan] {info['modificado']}")
            console.print(f"[cyan]URL:[/cyan] {info['url']}")
            console.print(Panel(info['texto'], title="📄 Resumo", expand=False))

    # Salvar JSON final
    with open("noticias.json", "w", encoding="utf-8") as f:
        json.dump(todas_noticias, f, ensure_ascii=False, indent=4)

    console.rule("[bold green]🏁 Coleta concluída — notícias salvas em noticias.json")
