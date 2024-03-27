# main.py
import streamlit as st
import cv2
import numpy as np
import pytesseract
import os
import time
import glob
from gtts import gTTS
from PIL import Image
from textblob import TextBlob
from googletrans import Translator
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# Función para convertir texto a audio
def text_to_speech(text, tld):
    tts = gTTS(text, lang="es", tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, text

# Función para eliminar archivos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

# Configuración de Streamlit
st.title("CocinaFacil - Tu Asistente de Cocina Personalizado")

# Opción de tomar foto o escribir frase
option = st.radio("Selecciona una opción:", ("Tomar Foto", "Escribir Frase"))

if option == "Tomar Foto":
    st.write(f"¡Hola! Puedes tomar una foto de la receta para convertirla en texto.")
    img_file_buffer = st.camera_input("Toma una Foto")

    with st.sidebar:
        filtro = st.radio("Aplicar Filtro", ('Con Filtro', 'Sin Filtro'))

    if img_file_buffer is not None:
        # Leer imagen
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Aplicar filtro si es seleccionado
        if filtro == 'Con Filtro':
             cv2_img = cv2.bitwise_not(cv2_img)
        else:
             cv2_img = cv2_img
            
        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        # Convertir imagen a texto
        text = pytesseract.image_to_string(img_rgb)
        st.write(text)

    # Botón para convertir texto a audio
    if st.button("Convertir receta a audio"):
        result, output_text = text_to_speech(text, "es")
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
        st.markdown(f"## Receta:")
        st.write(f" {output_text}")

elif option == "Escribir Frase":
    st.write("Puedes escribir una frase para obtener una recomendación de receta basada en tu estado de ánimo.")
    stt_button = Button(label="Comienza", width=200, button_type="success")

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0)

    if result:
        if "GET_TEXT" in result:
            st.subheader("Tu frase: ")
            st.write(result.get("GET_TEXT"))
        try:
            os.mkdir("temp")
        except:
            pass
        translator = Translator()

        text = str(result.get("GET_TEXT"))
        with st.expander('Analizar frase'):
            translation = translator.translate(text, src="es", dest="en")
            trans_text = translation.text
            blob = TextBlob(trans_text)
            st.write('Polarity: ', round(blob.sentiment.polarity,2))
            st.write('Subjectivity: ', round(blob.sentiment.subjectivity,2))
            x=round(blob.sentiment.polarity,2)
            if x >= 0.5:
                st.write('Es un sentimiento Positivo 😊')
                st.subheader("¡Te recomendamos probar esta receta positiva!")
                st.write("Nombre: Ensalada de quinoa con aguacate, tomate y aderezo de limón")
                st.write("Ingredientes:")
                st.write("- 1 taza de quinoa cocida")
                st.write("- 1 aguacate maduro, cortado en cubitos")
                st.write("- 1 tomate grande, cortado en cubitos")
                st.write("- Zumo de 1 limón")
                st.write("- Sal y pimienta al gusto")
                st.write("- Hojas de lechuga (opcional)")
                st.write("Preparación:")
                st.write("1. En un tazón grande, mezcla la quinoa cocida, el aguacate y el tomate.")
                st.write("2. Exprime el zumo de limón sobre la ensalada y sazona con sal y pimienta al gusto.")
                st.write("3. Opcionalmente, sirve sobre hojas de lechuga.")
            elif x <= -0.5:
                st.write('Es un sentimiento Negativo 😔')
                st.subheader("¡Te recomendamos probar esta receta reconfortante!")
                st.write("Nombre: Sopa de verduras reconfortante")
                st.write("Ingredientes:")
                st.write("- 2 zanahorias, cortadas en rodajas")
                st.write("- 2 ramas de apio, picadas")
                st.write("- 1 cebolla, picada")
                st.write("- 2 dientes de ajo, picados")
                st.write("- 1 papa grande, pelada y cortada en cubos")
                st.write("- 4 tazas de caldo de verduras")
                st.write("- Sal y pimienta al gusto")
                st.write("- Perejil fresco picado (opcional, para decorar)")
                st.write("Preparación:")
                st.write("1. En una olla grande, saltea la cebolla y el ajo en un poco de aceite hasta que estén dorados.")
                st.write("2. Agrega las zanahorias, el apio y la papa, y cocina por unos minutos.")
                st.write("3. Vierte el caldo de verduras, lleva a ebullición y luego reduce el fuego. Cocina a fuego lento hasta que las verduras estén tiernas.")
                st.write("4. Sazona con sal y pimienta al gusto.")
                st.write("5. Sirve caliente, decorado con perejil fresco si lo deseas.")
            else:
                st.write('Es un sentimiento Neutral 😐')
                st.subheader("¡Te recomendamos probar esta receta!")
                st.write("Nombre: Pasta con salsa de tomate y albahaca")
                st.write("Ingredientes:")
                st.write("- 250g de pasta de tu elección")
                st.write("- 2 tazas de salsa de tomate")
                st.write("- Un puñado de hojas de albahaca fresca")
                st.write("- Sal y pimienta al gusto")
                st.write("- Queso parmesano rallado (opcional, para servir)")
                st.write("Preparación:")
                st.write("1. Cocina la pasta según las instrucciones del paquete hasta que esté al dente. Escurre y reserva.")
                st.write("2. Calienta la salsa de tomate en una sartén grande.")
                st.write("3. Agrega las hojas de albahaca picadas y sazona con sal y pimienta al gusto.")
                st.write("4. Incorpora la pasta cocida a la salsa y mezcla bien.")
                st.write("5. Sirve caliente, con queso parmesano rallado si lo deseas.")

        # Eliminar archivos temporales
        remove_files(7)

# Footer
st.subheader("¡Ayúdanos a mejorar tu experiencia! Por favor, califica CocinaFacil:")
calificacion = st.slider("Califica de 1 a 5 estrellas", 1, 5)

if calificacion:
    st.write(f"¡Gracias por tu calificación de {calificacion} estrellas!")

