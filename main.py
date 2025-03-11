import streamlit as st
import fitz  # PyMuPDF
from gtts import gTTS
import pytesseract
from PIL import Image
import os
import io
import tempfile

# Set Tesseract path (update this path for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\DELL\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

st.title("📄 PDF to Speech Converter")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
page_range = st.text_input("Enter page number(s) or range (e.g., 1-3)")

if uploaded_file and page_range:
    try:
        # Load PDF
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        
        # Get page numbers
        pages = page_range.strip()
        if "-" in pages:
            first_page, last_page = map(int, pages.split("-"))
        else:
            first_page = int(pages)
            last_page = first_page
        
        # Extract text using OCR
        text = ""
        for i in range(first_page - 1, last_page):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            image = Image.open(io.BytesIO(pix.tobytes()))
            text += pytesseract.image_to_string(image, lang="eng") + "\n"
        
        # Display extracted text
        st.subheader("Extracted Text")
        st.text_area("", text, height=200)
        
        if text.strip():
            # Convert text to speech
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                tts.save(temp_audio.name)
                audio_path = temp_audio.name
            
            # Play and provide download option
            st.audio(audio_path, format='audio/mp3')
            st.download_button("Download Audio", data=open(audio_path, "rb"), file_name="pdf_audio.mp3", mime="audio/mp3")
        else:
            st.error("No text extracted. Try another page range.")
    except Exception as e:
        st.error(f"Error: {e}")
