# app.py

import streamlit as st
import openai
from pydub import AudioSegment
import tempfile
import os

# Configuración de la página
st.set_page_config(
    page_title="MP3 a Texto con OpenAI",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="auto",
)

# Título de la aplicación
st.title("🎤 Convertidor de MP3 a Texto usando OpenAI")

# Instrucciones
st.write("""
Sube un archivo de audio en formato MP3 y conviértelo a texto utilizando la potente API de OpenAI.
""")

# Carga del archivo
uploaded_file = st.file_uploader("Elige un archivo MP3", type=["mp3"])

if uploaded_file is not None:
    with st.spinner("Procesando..."):
        try:
            # Guardar el archivo subido en un archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                temp_mp3.write(uploaded_file.read())
                temp_mp3_path = temp_mp3.name

            # Convertir MP3 a WAV usando pydub (opcional, dependiendo de la API)
            audio = AudioSegment.from_mp3(temp_mp3_path)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                audio.export(temp_wav.name, format="wav")
                temp_wav_path = temp_wav.name

            # Configurar la clave de API de OpenAI desde los secretos de Streamlit
            openai.api_key = st.secrets["openai"]["api_key"]

            # Leer el archivo de audio
            with open(temp_wav_path, "rb") as audio_file:
                # Usar la API de transcripción de OpenAI (Whisper)
                transcript = openai.Audio.transcribe("whisper-1", audio_file)

            # Mostrar el texto transcrito
            st.success("¡Transcripción completada!")
            st.text_area("Texto Transcrito", transcript["text"], height=300)

            # Limpiar archivos temporales
            os.remove(temp_mp3_path)
            os.remove(temp_wav_path)

        except Exception as e:
            st.error(f"Ocurrió un error durante la transcripción: {e}")
