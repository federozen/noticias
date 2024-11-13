import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Scraper de Noticias Deportivas", layout="wide")
st.title("Scraper de Noticias Deportivas")
st.markdown("### Obtén los titulares de noticias deportivas desde varias fuentes.")

# Función para scrapeear titulares de una URL dada
def scrape_headlines(url, selector):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.select(selector)
        headlines = [element.get_text(strip=True) for element in elements if element.get_text(strip=True)]
        return headlines
    except requests.exceptions.RequestException as e:
        st.error(f"Error al acceder a {url}: {e}")
        return []
    except Exception as e:
        st.error(f"Error al procesar {url}: {e}")
        return []

# Diccionario con fuentes de noticias y sus selectores CSS
news_sources = {
    "BBC Deportes": {
        "url": "https://www.bbc.com/mundo/topics/cyx5krnw38vt",
        "selector": "h3.gs-c-promo-heading__title"
    },
    "Marca": {
        "url": "https://www.marca.com/futbol/",
        "selector": "a.title"
    },
    "ESPN": {
        "url": "https://www.espn.com.mx/futbol/",
        "selector": "h1.headline__title"
    }
}

# Selección de fuentes de noticias
selected_sources = st.multiselect(
    "Selecciona las fuentes de noticias:",
    options=list(news_sources.keys()),
    default=list(news_sources.keys())
)

# Botón para actualizar los datos
if st.button("Actualizar Titulares"):
    all_headlines = []
    for source in selected_sources:
        st.write(f"Scrapeando desde: **{source}**")
        url = news_sources[source]["url"]
        selector = news_sources[source]["selector"]
        headlines = scrape_headlines(url, selector)
        if headlines:
            df = pd.DataFrame(headlines, columns=["Titulares"])
            st.table(df)
        else:
            st.write("No se encontraron titulares.")

    st.success("Titulares actualizados correctamente.")
