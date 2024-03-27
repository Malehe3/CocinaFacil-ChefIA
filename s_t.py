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

st.title("CocinaFacil - Tu Asistente de Cocina Personalizado")
st.write("¡Hola! Soy ChefIA, tu asistente de cocina personal. Puedes elegir entre dos opciones: tomar una foto de una receta para que te la traduzca y lea en voz alta, o escribir una frase para que te recomiende una receta basada en tus sentimientos.")

option = st.radio("Selecciona una opción:", ("Tomar una Foto", "Escribir una Frase"))

# Función para convertir texto de imagen a voz y traducirlo
def convert_image_to_speech(image_file_buffer, filtro, language):
    bytes_data = image_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    if filtro == 'Con Filtro':
         cv2_img = cv2.bitwise_not(cv2_img)
    else:
         cv2_img = cv2_img
    
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    translator = Translator()
    translation = translator.translate(text, src='auto', dest=language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=language, slow=False)
    tts_filename = "temp/audio.mp3"
    tts.save(tts_filename)
    return text, tts_filename

# Función para analizar el estado de ánimo y recomendar una receta
def recommend_recipe(sentiment):
    if sentiment >= 0.5:
        recipe_name = "Ensalada de quinoa con aguacate, tomate y aderezo de limón"
        ingredients = ["1 taza de quinoa cocida", "1 aguacate maduro, cortado en cubitos", "1 tomate grande, cortado en cubitos", "Zumo de 1 limón", "Sal y pimienta al gusto", "Hojas de lechuga (opcional)"]
        preparation = ["En un tazón grande, mezcla la quinoa cocida, el aguacate y el tomate.", "Exprime el zumo de limón sobre la ensalada y sazona con sal y pimienta al gusto.", "Opcionalmente, sirve sobre hojas de lechuga."]
    elif sentiment <= -0.5:
        recipe_name = "Sopa de verduras reconfortante"
        ingredients = ["2 zanahorias, cortadas en rodajas", "2 ramas de apio, picadas", "1 cebolla, picada", "2 dientes de ajo, picados", "1 papa grande, pelada y cortada en cubos", "4 tazas de caldo de verduras", "Sal y pimienta al gusto", "Perejil fresco picado (opcional, para decorar)"]
        preparation = ["En una olla grande, saltea la cebolla y el ajo en un poco de aceite hasta que estén dorados.", "Agrega las zanahorias, el apio y la papa, y cocina por unos minutos.", "Vierte el caldo de verduras, lleva a ebullición y luego reduce el fuego. Cocina a fuego lento hasta que las verduras estén tiernas.", "Sazona con sal y pimienta al gusto.", "Sirve caliente, decorado con perejil fresco si lo deseas."]
    else:
        recipe_name = "Pasta con salsa de tomate y albahaca"
        ingredients = ["250g de pasta de tu elección", "2 tazas de salsa de tomate", "Un puñado de hojas de albahaca fresca", "Sal y pimienta al gusto", "Queso parmesano rallado (opcional, para servir)"]
        preparation = ["Cocina la pasta según las instrucciones del paquete hasta que esté al dente. Escurre y reserva.", "Calienta la salsa de tomate en una sartén grande.", "Agrega las hojas de albahaca picadas y sazona con sal y pimienta al gusto.", "Incorpora la pasta cocida a la salsa y mezcla bien.", "Sirve caliente, con queso parmesano rallado si lo deseas."]
    return recipe_name, ingredients, preparation

if option == "Tomar una Foto":
    img_file_buffer = st.file_uploader("Toma una Foto de la Receta", type=['jpg', 'png', 'jpeg'])
    if img_file_buffer is not None:
        language = st.selectbox("Selecciona el Idioma de la Traducción:", ("es", "en", "fr", "de", "it"))
        with st.sidebar:
            filtro = st.radio("Aplicar Filtro", ('Con Filtro', 'Sin Filtro'))
        text, audio_file = convert_image_to_speech(img_file_buffer, filtro, language)
        st.audio(audio_file, format="audio/mp3", start_time=0)
        st.write("Texto Extraído de la Imagen:")
        st.write(text)
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

        recipe_name, ingredients, preparation = recommend_recipe(sentiment)
        st.subheader(f"¡Te recomendamos probar esta receta {'' if sentiment == 0 else sentiment > 0 and 'positiva' or 'reconfortante'}!")
        st.write(f"Nombre: {recipe_name}")
        st.write("Ingredientes:")
        for ingredient in ingredients:
            st.write(f"- {ingredient}")
        st.write("Preparación:")
        for step in preparation:
            st.write(step)
