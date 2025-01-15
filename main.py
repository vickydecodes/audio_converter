from gtts import gTTS
import pygame
from pygame import mixer
from PIL import Image
import pytesseract
import os
import glob
import PySimpleGUI as sg
import fitz  # PyMuPDF


pytesseract.pytesseract.tesseract_cmd = r"C:\Users\DELL\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"


def get_text(value):
    string = value.strip()
    if "-" in string:
        first_page_number = int(string.split("-")[0])
        last_page_number = int(string.split("-")[1])
    else:
        first_page_number = int(string)
        last_page_number = 0
    return first_page_number, last_page_number

def main():
    # Create directory for Text to speech software
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, 'Text_to_speech_software')
    os.makedirs(final_directory, exist_ok=True)

    # GUI
    layout = [
        [sg.Text('Choose PDF File to read'), sg.Input(), sg.FileBrowse()],
        [sg.Text('Enter PDF Page number or range separated by - '), sg.InputText()],
        [sg.Button('Ok'), sg.Button('Cancel')]
    ]
    window = sg.Window('Input', layout)

    while True:
        event, values = window.read()
        pdf_to_read = values[0]
        if event in (None, 'Cancel'):
            window.close()
            exit()

        if event == "Ok":
            if not values[0]:
                sg.Popup("Enter PDF file to be transcribed")
            elif not values[1]:
                sg.Popup("Enter page number(s) to be transcribed")
            else:
                if not all(c.isdigit() or c == '-' for c in values[1]):
                    sg.Popup("Invalid value", "Enter valid page numbers")
                else:
                    break

    window.close()
    first_page_number, last_page_number = get_text(values[1])

    # Clear previous output files
    for file in os.listdir(final_directory):
        os.remove(os.path.join(final_directory, file))

    # Read PDF and save images
    doc = fitz.open(pdf_to_read)
    k = 1
    zoom_x, zoom_y = 2.0, 2.0
    mat = fitz.Matrix(zoom_x, zoom_y)

    if last_page_number == 0:
        page = doc.load_page(first_page_number - 1)
        pix = page.get_pixmap(matrix=mat)
        pix.save(os.path.join(final_directory, "image_to_read.png"))
    else:
        for i in range(first_page_number - 1, last_page_number):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=mat)
            pix.save(os.path.join(final_directory, f"image_{k}_to_read.png"))
            k += 1

    # Process images with OCR
    mytext = []
    for file in os.listdir(final_directory):
        data = pytesseract.image_to_string(Image.open(os.path.join(final_directory, file)), lang="eng")
        data = data.replace("|", "I").split('\n')
        mytext.extend(data)

    # Format text
    newtext = "\n".join(line.strip() for line in mytext if len(line.split()) >= 2)

    # Convert text to audio
    language = 'en'
    myobj = gTTS(text=newtext, lang=language, slow=False)
    audio_path = os.path.join(final_directory, "pdf_audio.mp3")
    myobj.save(audio_path)

    # Play audio
    pygame.init()
    mixer.init()
    mixer.music.load(audio_path)
    mixer.music.play()
    pygame.event.wait()

if __name__ == '__main__':
    main()
