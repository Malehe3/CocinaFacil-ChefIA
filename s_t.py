import os
import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator
from textblob import TextBlob
import pandas as pd
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# Función para eliminar archivos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

# Título de la aplicación
st.title("CocinaFacil - Tu Asistente de Cocina Personalizado")

# Función para convertir texto a audio
def text_to_speech(text, tld):
    tts = gTTS(text, lang="es", tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, text

# Función para convertir texto a audio con traducción
def translate_and_text_to_speech(text, input_language, output_language, tld):
    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

# Función para analizar sentimientos y recomendar recetas
def recommend_recipe(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity >= 0.5:
        recipe_name = "Ensalada de quinoa con aguacate, tomate y aderezo de limón"
        ingredients = ["1 taza de quinoa cocida", "1 aguacate maduro, cortado en cubitos", "1 tomate grande, cortado en cubitos", "Zumo de 1 limón", "Sal y pimienta al gusto", "Hojas de lechuga (opcional)"]
        steps = ["En un tazón grande, mezcla la quinoa cocida, el aguacate y el tomate.", "Exprime el zumo de limón sobre la ensalada y sazona con sal y pimienta al gusto.", "Opcionalmente, sirve sobre hojas de lechuga."]
    elif polarity <= -0.5:
        recipe_name = "Sopa de verduras reconfortante"
        ingredients = ["2 zanahorias, cortadas en rodajas", "2 ramas de apio, picadas", "1 cebolla, picada", "2 dientes de ajo, picados", "1 papa grande, pelada y cortada en cubos", "4 tazas de caldo de verduras", "Sal y pimienta al gusto", "Perejil fresco picado (opcional, para decorar)"]
        steps = ["En una olla grande, saltea la cebolla y el ajo en un poco de aceite hasta que estén dorados.", "Agrega las zanahorias, el apio y la papa, y cocina por unos minutos.", "Vierte el caldo de verduras, lleva a ebullición y luego reduce el fuego. Cocina a fuego lento hasta que las verduras estén tiernas.", "Sazona con sal y pimienta al gusto.", "Sirve caliente, decorado con perejil fresco si lo deseas."]
    else:
        recipe_name = "Pasta con salsa de tomate y albahaca"
        ingredients = ["250g de pasta de tu elección", "2 tazas de salsa de tomate", "Un puñado de hojas de albahaca fresca", "Sal y pimienta al gusto", "Queso parmesano rallado (opcional, para servir)"]
        steps = ["Cocina la pasta según las instrucciones del paquete hasta que esté al dente. Escurre y reserva.", "Calienta la salsa de tomate en una sartén grande.", "Agrega las hojas de albahaca picadas y sazona con sal y pimienta al gusto.", "Incorpora la pasta cocida a la salsa y mezcla bien.", "Sirve caliente, con queso parmesano rallado si lo deseas."]
    return recipe_name, ingredients, steps

# Interfaz de usuario para la conversión de imagen a texto y audio
st.subheader("Convertir receta de imagen a audio:")
img_file_buffer = st.file_uploader("Sube una foto de la receta")

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    img = Image.open(img_file_buffer)
    st.image(img, caption='Imagen subida', use_column_width=True)
    
    text = pytesseract.image_to_string(img)
    st.write("Texto extraído de la imagen:")
    st.write(text)

    if st.button("Convertir receta a audio"):
        result, output_text = text_to_speech(text, "es")
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
        st.markdown("## Receta:")
        st.write(output_text)

    remove_files(7)

# Interfaz de usuario para describir el estado de ánimo y recomendar una receta
st.subheader("Describir tu día y obtener una recomendación de receta:")
with st.expander('Analizar frase'):
    text = st.text_input('Escribe por favor: ')
    if text:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        st.write('Polarity: ', round(polarity, 2))
        st.write('Subjectivity: ', round(subjectivity, 2))
        if polarity >= 0.5:
            st.write('Es un sentimiento Positivo 😊')
        elif polarity <= -0.5:
            st.write('Es un sentimiento Negativo 😔')
        else:
            st.write('Es un sentimiento Neutral 😐')

        if st.button("Obtener recomendación de receta"):
            recipe_name, ingredients, steps = recommend_recipe(text)
            st.subheader("Receta recomendada:")
            st.write(f"Nombre: {recipe_name}")
            st.write("Ingredientes:")
            for ingredient in ingredients:
                st.write(f"- {ingredient}")
            st.write("Pasos:")
            for i, step in enumerate(steps, start=1):
                st.write(f"{i}. {step}")

# Eliminar archivos antiguos
remove_files(7)

