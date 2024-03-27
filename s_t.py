# main.py
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
import pandas as pd
from streamlit_bokeh_events import streamlit_bokeh_events

st.title("CocinaFacil - Tu Asistente de Cocina Personalizado")
st.write(f"¡Hola! Soy ChefIA, tu asistente de cocina personal. Con solo una foto de una receta, puedo convertirla en texto para que puedas escuchar las instrucciones mientras cocinas y así evitar cualquier accidente.")

# Opción para tomar una foto o escribir una frase
opcion = st.radio("Selecciona una opción:", ("Tomar Foto", "Escribir Frase"))

if opcion == "Tomar Foto":
    st.write("Por favor, toma una foto de la receta:")
    img_file_buffer = st.camera_input("Tomar Foto")

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        st.image(cv2_img, channels="RGB")

        text = pytesseract.image_to_string(cv2_img)
        st.write("Texto extraído de la imagen:")
        st.write(text)

elif opcion == "Escribir Frase":
    st.write("Escribe una frase que describa tu día:")
    frase = st.text_input("Frase:")

    if frase:
        translator = Translator()
        translation = translator.translate(frase, src="es", dest="en")
        trans_text = translation.text
        blob = TextBlob(trans_text)
        polarity = round(blob.sentiment.polarity, 2)

        if polarity >= 0.5:
            st.write("¡Es un sentimiento positivo! 😊")
            st.subheader("¡Te recomendamos probar esta receta positiva!")
            st.write("Nombre: Ensalada de quinoa con aguacate, tomate y aderezo de limón")
            # Añade los ingredientes y la preparación aquí
        elif polarity <= -0.5:
            st.write("¡Es un sentimiento negativo! 😔")
            st.subheader("¡Te recomendamos probar esta receta reconfortante!")
            st.write("Nombre: Sopa de verduras reconfortante")
            # Añade los ingredientes y la preparación aquí
        else:
            st.write("¡Es un sentimiento neutral! 😐")
            st.subheader("¡Te recomendamos probar esta receta!")
            st.write("Nombre: Pasta con salsa de tomate y albahaca")
            # Añade los ingredientes y la preparación aquí

# Función para convertir texto a audio
def text_to_speech(text, tld):
    tts = gTTS(text, lang="es", tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, text

# Botón para convertir texto a audio
if st.button("Convertir receta a audio"):
    result, output_text = text_to_speech(text, "es")
    audio_file = open(f"temp/{result}.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3", start_time=0)
    st.markdown(f"## Receta:")
    st.write(f" {output_text}")

# Limpieza de archivos temporales
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)



