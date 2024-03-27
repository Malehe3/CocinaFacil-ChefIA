import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import time
import glob
from gtts import gTTS
from googletrans import Translator
from textblob import TextBlob
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# Función para tomar una foto y traducirla
def take_photo_and_translate():
    st.title("CocinaFacil - Tomar una Foto y Traducir")
    st.write("¡Hola! Por favor, toma una foto de la receta que deseas traducir.")
    
    img_file_buffer = st.file_uploader("Carga una imagen", type=["jpg", "jpeg", "png"])

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.read()
        nparr = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        st.image(img, caption="Imagen cargada", use_column_width=True)

        with st.spinner("Procesando imagen..."):
            text = pytesseract.image_to_string(img)

        st.subheader("Texto extraído de la imagen:")
        st.write(text)

        translator = Translator()
        in_lang = st.selectbox(
            "Elige el idioma de origen:",
            ("Auto", "Inglés", "Español", "Alemán", "Francés", "Italiano")
        )

        if in_lang == "Auto":
            in_lang = None
        elif in_lang == "Inglés":
            in_lang = "en"
        elif in_lang == "Español":
            in_lang = "es"
        elif in_lang == "Alemán":
            in_lang = "de"
        elif in_lang == "Francés":
            in_lang = "fr"
        elif in_lang == "Italiano":
            in_lang = "it"

        out_lang = st.selectbox(
            "Elige el idioma de destino:",
            ("Inglés", "Español", "Alemán", "Francés", "Italiano")
        )

        if out_lang == "Inglés":
            out_lang = "en"
        elif out_lang == "Español":
            out_lang = "es"
        elif out_lang == "Alemán":
            out_lang = "de"
        elif out_lang == "Francés":
            out_lang = "fr"
        elif out_lang == "Italiano":
            out_lang = "it"

        translated_text = translator.translate(text, src=in_lang, dest=out_lang).text

        st.subheader("Texto traducido:")
        st.write(translated_text)

        # Función para convertir texto a audio
        def text_to_speech(text):
            tts = gTTS(text, lang=out_lang)
            try:
                file_name = "translated_audio.mp3"
            except:
                file_name = "translated_audio.mp3"
            tts.save(file_name)
            return file_name

        # Botón para convertir texto a audio
        if st.button("Convertir a audio"):
            audio_file_name = text_to_speech(translated_text)
            audio_file = open(audio_file_name, "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
            st.markdown("## Audio generado:")
            st.write(f" [Escuchar audio](./{audio_file_name})")

        os.remove("translated_audio.mp3")

# Función para escribir una frase y analizar sentimientos
def write_phrase_and_analyze_sentiment():
    st.title("CocinaFacil - Analizar Sentimientos")
    st.write("¡Hola! Por favor, escribe una frase para analizar tu estado de ánimo.")

    phrase = st.text_input("Escribe tu frase:")

    if phrase:
        translator = Translator()
        translation = translator.translate(phrase, src="es", dest="en")
        trans_text = translation.text
        blob = TextBlob(trans_text)
        polarity = blob.sentiment.polarity

        if polarity >= 0.5:
            st.write("¡Es un sentimiento positivo! 😊")
            st.write("¡Te recomendamos probar esta receta positiva!")
            st.write("Nombre: Ensalada de quinoa con aguacate, tomate y aderezo de limón")
            st.write("- 1 taza de quinoa cocida")
            st.write("- 1 aguacate maduro, cortado en cubitos")
            st.write("- 1 tomate grande, cortado en cubitos")
            st.write("- Zumo de 1 limón")
            st.write("- Sal y pimienta al gusto")
            st.write("- Hojas de lechuga (opcional)")
        elif polarity <= -0.5:
            st.write("¡Es un sentimiento negativo! 😔")
            st.write("¡Te recomendamos probar esta receta reconfortante!")
            st.write("Nombre: Sopa de verduras reconfortante")
            st.write("- 2 zanahorias, cortadas en rodajas")
            st.write("- 2 ramas de apio, picadas")
            st.write("- 1 cebolla, picada")
            st.write("- 2 dientes de ajo, picados")
            st.write("- 1 papa grande, pelada y cortada en cubos")
            st.write("- 4 tazas de caldo de verduras")
            st.write("- Sal y pimienta al gusto")
            st.write("- Perejil fresco picado (opcional, para decorar)")
        else:
            st.write("¡Es un sentimiento neutral! 😐")
            st.write("¡Te recomendamos probar esta receta!")
            st.write("Nombre: Pasta con salsa de tomate y albahaca")
            st.write("- 250g de pasta de tu elección")
            st.write("- 2 tazas de salsa de tomate")
            st.write("- Un puñado de hojas de albahaca fresca")
            st.write("- Sal y pimienta al gusto")
            st.write("- Queso parmesano rallado (opcional, para servir)")

# Función principal
def main():
    st.title("CocinaFacil - Tu Asistente de Cocina Personalizado")
    st.write("¡Bienvenido a CocinaFacil con ChefIA, tu asistente de cocina personal!")
    
    option = st.selectbox("Elige una opción:", ("Tomar una foto y traducir", "Escribir una frase y analizar sentimientos"))

    if option == "Tomar una foto y traducir":
        take_photo_and_translate()
    elif option == "Escribir una frase y analizar sentimientos":
        write_phrase_and_analyze_sentiment()

# Llamar a la función principal
if __name__ == "__main__":
    main()


