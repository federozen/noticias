import requests
from bs4 import BeautifulSoup

def obtener_html(url):
    """
    Obtiene el contenido HTML de una URL.

    Args:
        url (str): La URL de la página web a descargar.

    Returns:
        str: El contenido HTML de la página, o None si hay un error.
    """
    try:
        headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/91.0.4472.124 Safari/537.36')
        }
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.raise_for_status()  # Lanza excepción para errores 4xx o 5xx
        return respuesta.text
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página: {e}")
        return None

def extraer_titulos_noticias(html):
    """
    Extrae los títulos de noticias de una página HTML.

    Args:
        html (str): El contenido HTML de la página.

    Returns:
        list: Lista de títulos de noticias encontrados.
    """
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    titulos = []

    # Buscar títulos en etiquetas h1, h2, h3
    for titulo in soup.find_all(["h1", "h2", "h3"]):
        texto = titulo.get_text(strip=True)
        if texto and len(texto) > 16:
            titulos.append(texto)

    # Buscar títulos en clases específicas comunes en medios
    for elemento in soup.select(".title, .headline, .article-title, .news-title"):
        texto = elemento.get_text(strip=True)
        if texto and texto not in titulos:
            titulos.append(texto)

    return titulos

# Diccionario con medios de comunicación y sus respectivas URL
medios = {
    "Ole": "https://www.ole.com.ar/",
    "Clarin deportes": "https://www.clarin.com/deportes",
    "Espn": "https://www.espn.com.ar/",
    "Doble Amarilla": "https://www.dobleamarilla.com.ar/",
    "TyC Sports": "https://www.tycsports.com/",
    "Infobae": "https://www.infobae.com/deportes/",
    "La Nacion": "https://www.lanacion.com.ar/deportes/",
    "TN": "https://tn.com.ar/deportes/",
    "Cielo": "https://infocielo.com/cielosports",
    "Capital Rosario": "https://www.lacapital.com.ar/secciones/ovacion.html",
    "Bolavip": "https://bolavip.com/ar",
    "La Voz": "https://www.lavoz.com.ar/deportes/",
    "As": "https://as.com/",
    "Marca": "https://www.marca.com/",
    "Mundo Deportivo": "https://www.mundodeportivo.com/",
    "Sport": "https://www.sport.es/es/",
    "Globoesporte": "https://ge.globo.com/",
    "La Tercera": "https://www.latercera.com/canal/el-deportivo/",
    "Referi Uruguay": "https://www.elobservador.com.uy/referi",

}

def main():
    print("Scraping de Títulos de Noticias")
    print("Este es un ejemplo de scraping de títulos de noticias de varios medios.\n")

    for nombre, url in medios.items():
        print("=" * 80)
        print(f"Fuente: {nombre} - {url}")
        print(f"Scrapeando {nombre}...\n")
        html = obtener_html(url)
        titulos = extraer_titulos_noticias(html)
        # Limitar a 30 titulares para cada medio
        titulos = titulos[:30]
        if titulos:
            print("Títulos de noticias:")
            for titulo in titulos:
                print(f"{nombre} | {titulo}")
        else:
            print("No se encontraron títulos de noticias.")
        print("\n")

if __name__ == "__main__":
    main()
