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
        res = requests.get(url, timeout=10)
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
            if isinstance(headline_selector, list):
                # Manejo de múltiples selectores
                headlines = []
                for selector in headline_selector:
                    elements = soup.select(selector)
                    for element in elements:
                        if title_attribute == "text":
                            headline = element.get_text()
                        else:
                            headline = element.get(title_attribute)
                        if headline:
                            headlines.append(headline.strip())
            else:
                elements = soup.select(headline_selector)
                headlines = []
                for element in elements:
                    if title_attribute == "text":
                        headline = element.get_text()
                    else:
                        headline = element.get(title_attribute)
                    if headline:
                        headlines.append(headline.strip())

        return headlines[:limit]

    except requests.exceptions.RequestException as e:
        st.error(f"Error scraping {url}: {e}")
        return []
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al scrapear {url}: {e}")
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
        "selector": ["h2.bstn-hl-title.gui-color-primary.gui-color-hover.gui-color-primary-bg-after", "h2", "h1"],
        "limit": 20
    },
    "La Tercera de Chile": {"url": "https://www.latercera.com/canal/el-deportivo/", "selector": "h6", "limit": 20},
    "Observador Uruguay": {"url": "https://www.elobservador.com.uy/referi", "selector": "h2.titulo", "limit": 15},
    "Record Portugal": {
        "url": "https://www.record.pt/",
        "selector": ["h1", "h2", "h3"],
        "limit": [5, 10, 10],
        "start_index": [1, 0, 0]
    },
    "BBC": {"url": "https://www.bbc.com/sport", "selector": "h1", "limit": 20},
    "Sky Sports": {"url": "https://www.skysports.com/", "selector": "h3", "limit": 25},
    "Gazzetta dello Sport": {"url": "https://www.gazzetta.it/", "selector": "h3", "limit": 20},
    "Lequipe": {"url": "https://www.lequipe.fr/", "selector": "h2", "limit": 20},
}

# Lista para almacenar todos los titulares
all_headlines = []

st.set_page_config(page_title="Titulares de Noticias Deportivas", layout="wide")
st.title("Titulares de Noticias Deportivas")
st.markdown("### Aquí encontrarás los titulares de noticias deportivas scrapeados desde varias fuentes.")

# Opciones de usuario en la barra lateral
st.sidebar.header("Opciones")
selected_sources = st.sidebar.multiselect(
    "Selecciona las fuentes de noticias:",
    options=list(news_sources.keys()),
    default=list(news_sources.keys())
)
refresh = st.sidebar.button("Actualizar")

@st.cache_data(ttl=3600)
def get_headlines(selected_sources):
    all_headlines = []
    for source_name in selected_sources:
        source_data = news_sources[source_name]
        url = source_data["url"]
        selector = source_data.get("selector", "h2")
        limit = source_data.get("limit", 15)
        start_index = source_data.get("start_index", 0)
        num_to_fetch = source_data.get("num_to_fetch", None)
        club_names = source_data.get("club_names", None)

        # Manejo de múltiples selectores y límites
        if isinstance(selector, list):
            headlines = []
            for i, sel in enumerate(selector):
                lim = limit[i] if isinstance(limit, list) else limit
                st_index = start_index[i] if isinstance(start_index, list) else start_index
                hl = scrape_news(
                    url,
                    sel,
                    limit=lim,
                    start_index=st_index,
                    num_to_fetch=num_to_fetch,
                    club_names=club_names
                )
                headlines.extend(hl)
        else:
            headlines = scrape_news(
                url,
                selector,
                limit=limit,
                start_index=start_index,
                num_to_fetch=num_to_fetch,
                club_names=club_names
            )

        all_headlines.extend([(source_name, headline) for headline in headlines if headline])

    df = pd.DataFrame(all_headlines, columns=["Fuente", "Titular"])
    return df

if refresh:
    st.cache_data.clear()
    st.experimental_rerun()

# Obtener los titulares
df = get_headlines(selected_sources)

# Mostrar el DataFrame en Streamlit
st.dataframe(df, use_container_width=True)

# Opcional: Descargar el DataFrame como CSV
st.download_button(
    label="Descargar CSV",
    data=df.to_csv(index=False, encoding='utf-8'),
    file_name="titulares_deportivos.csv",
    mime="text/csv"
)
