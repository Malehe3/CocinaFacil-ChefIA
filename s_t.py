import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob

from gtts import gTTS
from googletrans import Translator

st.title("CocinaFacil - Tu Asistente de Cocina Personalizado")

image = Image.open('RatitaChef3.png')
st.image(image, width=200)

st.write("¡Bienvenido a CocinaFacil con ChefIA, tu asistente de cocina personal! Aquí podrás narrar tus recetas para que otras personas hasta de diferentes partes del mundo, puedan conocer y disfrutar al máximo de tus creaciones culinarias.")

st.subheader("Pulsa el botón y compártenos tu receta")

stt_button = Button(label="Comienza", width=200, button_type="success")
#Button(label="Comienza", width=200, button_type="success")

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
        st.subheader("Tu receta: ")
        st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except:
        pass
    translator = Translator()

    text = str(result.get("GET_TEXT"))
    in_lang = st.selectbox(
        "Elige el idioma en el que compartiste tu receta",
        ("Inglés", "Español", "Alemán", "Francés", "Bengalí", "Coreano", "Mandarín", "Japonés"),
    )
    if in_lang == "Inglés":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Alemán":
        input_language = "de"
    elif in_lang == "Francés":
        input_language = "fr"
    elif in_lang == "Bengalí":
        input_language = "bn"
    elif in_lang == "Coreano":
        input_language = "ko"
    elif in_lang == "Mandarín":
        input_language = "zh-cn"
    elif in_lang == "Japonés":
        input_language = "ja"

    out_lang = st.selectbox(
        "Elige el idioma en el que quieres compartartir tu receta",
        ("Inglés", "Español", "Alemán", "Francés", "Bengalí", "Coreano", "Mandarín", "Japonés"),
    )
    if out_lang == "Inglés":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Alemán":
        output_language = "de"
    elif out_lang == "Francés":
        output_language = "fr"
    elif out_lang == "Bengalí":
        output_language = "bn"
    elif out_lang == "Coreano":
        output_language = "ko"
    elif out_lang == "Mandarín":
        output_language = "zh-cn"
    elif out_lang == "Japonés":
        output_language = "ja"

    english_accent = st.selectbox(
        "Elige un acento",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canada",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
    )

    if english_accent == "Defecto":
        tld = "com"
    elif english_accent == "Español":
        tld = "com.mx"
    elif english_accent == "Reino Unido":
        tld = "co.uk"
    elif english_accent == "Estados Unidos":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Irlanda":
        tld = "ie"
    elif english_accent == "Sudáfrica":
        tld = "co.za"


    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text


    display_output_text = st.checkbox("Mostrar el texto")

    if st.button("Aceptar"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tú audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.write(f"### Ahora puedes compartir tu receta con más personas")
            st.write(f" {output_text}")


    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)
    st.subheader("¡Ayúdanos a mejorar tu experiencia! Por favor, califica CocinaFacil:")
    calificacion = st.slider("Califica de 1 a 5 estrellas", 1, 5)

    if calificacion:
        st.write(f"¡Gracias por tu calificación de {calificacion} estrellas!")


