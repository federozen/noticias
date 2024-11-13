import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Función para scrapear noticias de una URL dada
def scrape_news(url, headline_selector, title_attribute="text", fallback_attribute="text", limit=15, club_names=None, start_index=0, num_to_fetch=None):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")
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
            headlines = []
            elements = soup.select(headline_selector)
            for element in elements:
                if title_attribute == "text":
                    headline = element.get_text()
                else:
                    headline = element.get(title_attribute)
                if headline:
                    headlines.append(headline.strip())
                else:
                    if fallback_attribute == "text":
                        headline = element.get_text()
                    else:
                        headline = getattr(element, fallback_attribute, None)
                    if headline:
                        headlines.append(headline.strip())

        return headlines[:limit]

    except requests.exceptions.RequestException as e:
        st.error(f"Error al scrapear {url}: {e}")
        return []
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al scrapear {url}: {e}")
        return []

# Club names to exclude from TyC Sports
club_names = [
    "Argentinos Juniors", "Atlético Tucumán", "Banfield", "Barracas Central", "Belgrano",
    "Boca Juniors", "Central Córdoba (Santiago del Estero)", "Colón", "Defensa y Justicia",
    "Estudiantes (La Plata)", "Gimnasia (La Plata)", "Godoy Cruz", "Huracán", "Independiente",
    "Instituto", "Lanús", "Newell's", "Platense", "Racing Club", "River Plate",
    "Rosario Central", "San Lorenzo", "Sarmiento (J)", "Talleres (Córdoba)", "Tigre",
    "Unión", "Vélez"
]

# Fuentes de noticias
news_sources = {
    "Ole": {"url": "https://www.ole.com.ar/", "selector": "h2.sc-fa18824-3", "limit": 30},
    "TyC": {
        "url": "https://www.tycsports.com/",
        "selector": "img[alt]",
        "club_names": club_names,
        "start_index": 22,
        "num_to_fetch": 21,
        "limit": 15
    },
    "La Nación": {"url": "https://www.lanacion.com.ar/deportes/", "selector": "h2.com-title", "limit": 15},
    "ESPN": {"url": "https://www.espn.com.ar/", "selector": "h2"},
    "Infobae": {"url": "https://www.infobae.com/deportes/", "selector": "h2", "limit": 15},
    "Clarín": {
        "url": "https://www.clarin.com/deportes/",
        "selector": "article.sc-a70022fc-0.gjbWNc a",
        "title_attribute": "aria-label",
        "fallback_attribute": "text",
        "limit": 15
    },
    "Doble Amarilla": {"url": "https://www.dobleamarilla.com.ar/", "selector": ".title span"},
    "UEFA": {"url": "https://es.uefa.com/", "selector": "h2", "limit": 20},
    "La Voz": {"url": "https://www.lavoz.com.ar/deportes/", "selector": "h2"},
    "Cielo Sports": {"url": "https://infocielo.com/deportes", "selector": "h2", "limit": 15},
    "Bola Vip": {"url": "https://bolavip.com/ar", "selector": "h2", "limit": 25},
    "TN Deportivo": {"url": "https://tn.com.ar/deportes/", "selector": "h2.card__headline", "limit": 15},
    "Pagina Millonaria": {"url": "https://lapaginamillonaria.com/", "selector": "h1, h2"},
    "Racingdealma": {"url": "https://www.racingdealma.com.ar/", "selector": "h3 a", "limit":12},
    "Infierno Rojo": {"url": "https://www.infiernorojo.com/independiente/", "selector": "h2", "limit": 15},
    "Mundo Azulgrana": {"url": "https://mundoazulgrana.com.ar/sanlorenzo/", "selector": "h1, h2, h3"},
}

# Configuración de la página de Streamlit
st.set_page_config(page_title="Titulares de Noticias de Fútbol", layout="wide")
st.title("Titulares de Noticias de Fútbol")
st.markdown("Aquí encontrarás los titulares de noticias de fútbol scrapeados desde varias fuentes.")

# Opciones de usuario
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
        headlines = scrape_news(
            source_data["url"],
            source_data.get("selector", "h2"),
            title_attribute=source_data.get("title_attribute", "text"),
            fallback_attribute=source_data.get("fallback_attribute", "text"),
            limit=source_data.get("limit", 15),
            club_names=source_data.get("club_names"),
            start_index=source_data.get("start_index", 0),
            num_to_fetch=source_data.get("num_to_fetch")
        )
        all_headlines.extend([(source_name, headline) for headline in headlines if headline])
    df = pd.DataFrame(all_headlines, columns=["Fuente", "Titular"])
    return df

if refresh:
    # Limpiar la caché para forzar la actualización
    st.cache_data.clear()
    st.experimental_rerun()

# Obtener los titulares
df = get_headlines(selected_sources)

# Mostrar el DataFrame
st.dataframe(df, use_container_width=True)

# Opcional: Descargar el DataFrame como CSV
st.download_button(
    label="Descargar CSV",
    data=df.to_csv(index=False, encoding='utf-8'),
    file_name="noticias_deportivas.csv",
    mime="text/csv"
)
