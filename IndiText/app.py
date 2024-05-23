from flask import Flask, request, render_template
import os
from importlib_metadata import files
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from googletrans import Translator,LANGUAGES
from werkzeug.utils import secure_filename
from flask import jsonify
from PyPDF2 import PdfReader, PdfWriter 
from langdetect import detect
from pdfminer.high_level import extract_text


#import docx

app = Flask(__name__)

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'venv/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf','docx' }

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=[ 'POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # Check if file is uploaded
        if 'file' not in request.files:
            return 'No file uploaded!'
        file = request.files['file']
        # Check if file is selected
        if file.filename == '':
            return 'No selected file!'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            if filename.endswith('.txt'):
                extracted_info = extract_info(filepath)
            elif filename.endswith('.pdf'):
                extracted_info = extract_PDF(filepath)
            elif filename.endswith('.docx'):
                extracted_info = extract_docx(filepath)
            sel=request.form['language']
            translated_text=translate_text(extracted_info,sel)
            return render_template('upload.html', extracted_info=translated_text)
    return render_template('upload.html')

# Replace this function with your logic to extract information from the file
def extract_info(filepath):
    with open(filepath, 'r',encoding='utf-8') as f:
        # Read and process the file content as needed
        lines = f.readlines()
        # Example: extract first line as info
        info = lines[0].strip()
        return info

# Replace this function with your logic to extract information from the pdf

def extract_PDF(file_path):
    text = extract_text(file_path)
    return text


def generate_pdf(translation):
        output_path = 'venv/uploads/translated_file.pdf'
        pdf_writer = PdfWriter()
        pdf_writer.add_page()
        pdf_writer.set_font("Arial", size=12)
        pdf_writer.cell(200, 10, txt=translation, ln=1)
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        return output_path



def translate_text(txt,lg):
    #text_to_translate = request.form.get('text')
    v=detect(txt)
    #source_language = request.form.get('source_language')
    target_language = request.form.get('target_language')
    t=str(txt)
    lm={'telugu':'te','tamil':'ta','kannada':'kn','bengali':'bn','hindi':'hi','malayalam':'ml','marathi':'mr','gujarati':'gu','punjabi':'pa','urdu':'ur','sindhi':'sd','nepali':'ne','assamese':'as','oriya':'or','english':'en'}
    vl=list(lm.values())
    kl=list(lm.keys())
    i=vl.index(v)
    k=kl[i]
    translator = Translator()
    try:
        translation = translator.translate(t, src=k, dest=lm[lg]).text
        print(f"Translation: {translation}")
        
    except Exception as e:
        print(f"Translation error: {e}")
        translation = "Translation failed. Please try again later."

    #return jsonify({'translation': translation})
    return translation




if __name__ == '__main__':
    app.run(debug=True)
