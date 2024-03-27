import streamlit as st
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator
from textblob import TextBlob

st.title("CocinaFacil - Tu Asistente de Cocina Personalizado")
st.write("¡Hola! Soy ChefIA, tu asistente de cocina personal. Puedes elegir entre dos opciones: tomar una foto de una receta para que te la traduzca y lea en voz alta, o escribir una frase para que te recomiende una receta basada en tus sentimientos.")

option = st.radio("Selecciona una opción:", ("Tomar una Foto", "Escribir una Frase"))

# Función para convertir texto a voz
def text_to_speech(text, language):
    tts = gTTS(text, lang=language, slow=False)
    tts_filename = "temp/audio.mp3"
    tts.save(tts_filename)
    return tts_filename

# Función para traducir texto
def translate_text(text, language):
    translator = Translator()
    translation = translator.translate(text, src='auto', dest=language)
    return translation.text

if option == "Tomar una Foto":
    img_file_buffer = st.file_uploader("Toma una Foto de la Receta", type=['jpg', 'png', 'jpeg'])
    if img_file_buffer is not None:
        language = st.selectbox("Selecciona el Idioma de la Traducción:", ("es", "en", "fr", "de", "it"))
        with st.sidebar:
            filtro = st.radio("Aplicar Filtro", ('Con Filtro', 'Sin Filtro'))

        bytes_data = img_file_buffer.getvalue()
        img = Image.open(io.BytesIO(bytes_data))
        
        if filtro == 'Con Filtro':
            img = img.convert("L")  # Convertir a escala de grises
            
        text = pytesseract.image_to_string(img)
        translated_text = translate_text(text, language)
        st.write("Texto Extraído de la Imagen:")
        st.write(translated_text)
        
        audio_file = text_to_speech(translated_text, language)
        st.audio(audio_file, format="audio/mp3", start_time=0)

else:
    st.markdown("### Escribir una Frase")
    text = st.text_input('Describe tu día en una frase:')
    if text:
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        if sentiment >= 0.5:
            st.write('Es un sentimiento Positivo 😊')
        elif sentiment <= -0.5:
            st.write('Es un sentimiento Negativo 😔')
        else:
            st.write('Es un sentimiento Neutral 😐')

        # Lógica para recomendar una receta basada en el sentimiento
        # Aquí podrías incluir la recomendación de recetas basadas en el sentimiento del usuario

