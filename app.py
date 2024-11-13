import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Función para scrapear noticias de una URL dada
def scrape_news(url, headline_selector, title_attribute="text", limit=15, club_names=None, start_index=0, num_to_fetch=None):
    """
    Scrapes news headlines from a given URL and returns them as a list.

    Args:
        url: The URL of the news website.
        headline_selector: A CSS selector to find headline elements.
        title_attribute: The attribute to extract from the headline element (default: 'text').
        limit: The maximum number of headlines to scrape (default: 15).
        club_names: A list of club names to exclude from TyC Sports scraping (optional).
        start_index: The starting index for scraping headlines (default: 0).
        num_to_fetch: The number of headlines to fetch (optional).

    Returns:
        A list of scraped headlines.
    """
    try:
        # Realizar solicitud GET a la URL
        res = requests.get(url)
        res.raise_for_status()

        # Parsear contenido HTML con BeautifulSoup
        soup = BeautifulSoup(res.content, "html.parser")

        # Lógica para TyC Sports (si aplica)
        if club_names and "tycsports" in url.lower():
            titulos = soup.find_all("img", alt=True)
            headlines = []
            for titulo in titulos[start_index:start_index + num_to_fetch]:
                found = False
                for club_name in club_names:
                    if club_name.lower() in titulo["alt"].lower():
                        found = True
                        break
                if not found:
                    headlines.append(titulo["alt"])
        else:
            # Selección de titulares mediante CSS selector
            headlines = soup.select(headline_selector)
            headlines = [getattr(headline, title_attribute).strip() for headline in headlines if getattr(headline, title_attribute)]

        return headlines[:limit]

    except requests.exceptions.RequestException as e:
        st.error(f"Error scraping {url}: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while scraping {url}: {e}")
        return []

# Fuentes de noticias con sus respectivos selectores y límites
news_sources = {
    "As": {"url": "https://argentina.as.com/", "selector": "h2", "limit": 20, "start_index": 1},
    "Marca": {"url": "https://www.marca.com/?intcmp=BOTONPORTADA&s_kw=portada&ue_guest/", "selector": "h2", "limit": 20, "start_index": 1},
    "Mundo Deportivo": {"url": "https://www.mundodeportivo.com/", "selector": "h2", "limit": 20},
    "Sport": {"url": "https://www.sport.es/", "selector": "h2.title", "limit": 15},
    "Relevo": {"url": "https://www.relevo.com/", "selector": "h2", "limit": 20, "start_index": 1},
    "Globo Esporte": {
        "url": "https://ge.globo.com/",
        "selectors": ["h2.bstn-hl-title.gui-color-primary.gui-color-hover.gui-color-primary-bg-after", "h2", "h1"]
    },
    "La Tercera de Chile": {"url": "https://www.latercera.com/canal/el-deportivo/", "selector": "h6", "limit": 20},
    "Observador Uruguay": {"url": "https://www.elobservador.com.uy/referi", "selector": "h2.titulo"},
    "Record Portugal": {
        "url": "https://www.record.pt/",
        "selectors": ["h1", "h2", "h3"],
        "limits": [5, 10, 10],
        "start_index": [1, 0, 0]
    },
    "BBC": {"url": "https://www.bbc.com/sport", "selector": "h1", "limit": 20},
    "Sky Sports": {"url": "https://www.skysports.com/", "selector": "h3", "limit": 25},
    "Gazzetta dello Sport": {"url": "https://www.gazzetta.it/", "selector": "h3", "limit": 20},
    "Lequipe": {"url": "https://www.lequipe.fr/", "selector": "h2", "limit": 20},
}

# Configuración de la aplicación Streamlit
st.title("Scraping de Noticias de Fuentes Varias")

# Lista para almacenar todos los titulares
all_headlines = []

# Iterar sobre fuentes de noticias y scrapear titulares
for source_name, source_data in news_sources.items():
    st.write(f"\n--- {source_name} ---\n")

    if 'selectors' in source_data:
        # Manejo de múltiples selectores para una sola fuente
        for i, selector in enumerate(source_data['selectors']):
            limit = source_data.get('limits', [15])[i] if 'limits' in source_data else 15
            start_index = source_data.get('start_index',  <sup> </sup>)[i] if 'start_index' in source_data else 0
            headlines = scrape_news(source_data["url"], selector, limit=limit, start_index=start_index)
            all_headlines.extend([(source_name, headline) for headline in headlines])
    else:
        # Scrapear titulares con selector único
        headlines = scrape_news(
            source_data["url"],
            source_data.get("selector", "h2"),
            limit=source_data.get("limit", 15),
            start_index=source_data.get("start_index", 0)
        )
        all_headlines.extend([(source_name, headline) for headline in headlines])

    # Imprimir titulares scrapeados para cada fuente
    if headlines:
        for headline in headlines:
            st.write(headline)
    else:
        st.write(f"\nNo headlines found for {source_name}\n")

# Crear DataFrame con todos los titulares scrapeados
df = pd.DataFrame(all_headlines, columns=["Source", "Headline"])

# Mostrar DataFrame
st.write("\n--- Todos los Titulares ---\n")
st.dataframe(df)

# Guardar DataFrame en archivo CSV (opcional)
csv = df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="scrapeados.csv",
    mime="text/csv"
)
