import streamlit as st
import fitz  # PyMuPDF
import pytesseract
import pyttsx3  # Offline TTS
from PIL import Image
import io
import tempfile
import time
import googletrans
from googletrans import Translator
import zipfile

# Set Tesseract path (update for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\DELL\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

st.title("📄 PDF to Speech Converter")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    # Load PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    total_pages = len(doc)
    
    # Page selection
    page_number = st.number_input("Select Page to Read", min_value=1, max_value=total_pages, step=1, value=1)
    
    # Voice, speed, pitch, and volume options
    voice_choice = st.radio("Select Voice:", ["Male", "Female"])
    speed_option = st.slider("Select Speed", 50, 200, 150)  # Default = 150
    pitch_option = st.slider("Select Pitch", 50, 200, 100)  # Default = 100 (Neutral pitch)
    volume_option = st.slider("Select Volume", 0.1, 1.0, 1.0)  # Volume control
    
    # Translation options
    translator = Translator()
    lang_options = list(googletrans.LANGUAGES.values())
    selected_lang = st.selectbox("Select Language for Translation (Optional)", ["None"] + lang_options)
    
    if st.button("Convert to Speech"):
        try:
            with st.spinner("📖 Extracting text from PDF..."):
                time.sleep(1)  # Simulating loading
                
                # Extract text using OCR
                page = doc.load_page(page_number - 1)
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                image = Image.open(io.BytesIO(pix.tobytes()))
                text = pytesseract.image_to_string(image, lang="eng")
            
            if text.strip():
                st.subheader("📜 Extracted Text")
                st.write(text)
                
                # Save extracted text
                eng_text_path = tempfile.mktemp(suffix="_eng_extraction.txt")
                with open(eng_text_path, "w", encoding="utf-8") as f:
                    f.write(text)
                
                # Translate if language is selected
                translated_text_path = None
                if selected_lang != "None":
                    target_lang = list(googletrans.LANGUAGES.keys())[lang_options.index(selected_lang)]
                    translated_text = translator.translate(text, dest=target_lang).text
                    st.subheader("🌍 Translated Text")
                    st.write(translated_text)
                    
                    translated_text_path = tempfile.mktemp(suffix=f"_{selected_lang}_extraction.txt")
                    with open(translated_text_path, "w", encoding="utf-8") as f:
                        f.write(translated_text)
                else:
                    translated_text = text
                
                # Text-to-Speech Setup
                temp_audio_path = tempfile.mktemp(suffix=".mp3")
                
                engine = pyttsx3.init()
                voices = engine.getProperty("voices")
                engine.setProperty("voice", voices[0].id if voice_choice == "Male" else voices[1].id)
                engine.setProperty("rate", speed_option)
                engine.setProperty("pitch", pitch_option)  # Set pitch
                engine.setProperty("volume", volume_option)  # Set volume
                engine.save_to_file(translated_text, temp_audio_path)
                engine.runAndWait()
                
                # Create zip file
                zip_path = tempfile.mktemp(suffix=".zip")
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    zipf.write(eng_text_path, "eng_extraction.txt")
                    if translated_text_path:
                        zipf.write(translated_text_path, f"{selected_lang}_extraction.txt")
                    zipf.write(temp_audio_path, "speech.mp3")
                
                # Provide download option
                with open(zip_path, "rb") as f:
                    st.download_button("📥 Download All (ZIP)", data=f, file_name="pdf_speech_package.zip", mime="application/zip")
            else:
                st.error("⚠️ No text extracted from this page.")
        except Exception as e:
            st.error(f"❌ Error: {e}")