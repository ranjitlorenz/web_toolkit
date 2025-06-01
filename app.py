<<<<<<< HEAD
from flask import Flask, request, render_template_string, send_file
import os
import subprocess
import whisper # Assuming you have it installed
import fitz # For PyMuPDF, install with pip install PyMuPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Whisper model globally (similar to your Tkinter app)
# Be aware: 'medium' or 'large' models can be heavy for free tiers.
# The model will download on first deploy if not cached by Render/Railway.
try:
    whisper_model = whisper.load_model("small")
except Exception as e:
    print(f"Error loading Whisper model at startup: {e}")
    whisper_model = None # Handle this gracefully in transcription function

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Conversion & Transcription Tools</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
        input[type="file"] { margin-bottom: 10px; }
        button { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        textarea { width: 100%; height: 150px; margin-top: 10px; padding: 10px; border-radius: 4px; border: 1px solid #ddd; resize: vertical; }
        .result { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web Tools</h1>

        <h2>Audio Transcription</h2>
        <form method="post" enctype="multipart/form-data" action="/transcribe">
            <input type="file" name="audio_file" accept="audio/*">
            <button type="submit">Transcribe Audio</button>
        </form>
        {% if transcription_result %}
        <div class="result">
            <h3>Transcription:</h3>
            <textarea readonly>{{ transcription_result }}</textarea>
        </div>
        {% endif %}

        <h2>PDF to TXT Conversion</h2>
        <form method="post" enctype="multipart/form-data" action="/pdf-to-txt">
            <input type="file" name="pdf_file" accept=".pdf">
            <button type="submit">Convert PDF to TXT</button>
        </form>
        {% if pdf_conversion_result %}
        <div class="result">
            <h3>PDF Text:</h3>
            <textarea readonly>{{ pdf_conversion_result }}</textarea>
        </div>
        {% endif %}

        {% if error_message %}
        <div class="result" style="color: red;">
            <h3>Error:</h3>
            <p>{{ error_message }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio_file' not in request.files:
        return render_template_string(HTML_TEMPLATE, error_message="No audio file part")
    file = request.files['audio_file']
    if file.filename == '':
        return render_template_string(HTML_TEMPLATE, error_message="No selected audio file")
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        if whisper_model is None:
            return render_template_string(HTML_TEMPLATE, error_message="Whisper model not loaded. Please try again later.")

        try:
            # Whisper will auto-detect language
            result = whisper_model.transcribe(file_path)
            transcription = result.get("text", "Transcription failed.")
            return render_template_string(HTML_TEMPLATE, transcription_result=transcription)
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error_message=f"Transcription error: {e}. Ensure FFmpeg is correctly installed on the server.")
        finally:
            os.remove(file_path) # Clean up uploaded file

@app.route('/pdf-to-txt', methods=['POST'])
def pdf_to_txt():
    if 'pdf_file' not in request.files:
        return render_template_string(HTML_TEMPLATE, error_message="No PDF file part")
    file = request.files['pdf_file']
    if file.filename == '':
        return render_template_string(HTML_TEMPLATE, error_message="No selected PDF file")
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        try:
            # Example using PyMuPDF (fitz)
            # You'd need `pip install PyMuPDF` in your requirements.txt
            import fitz # Import inside to avoid error if not installed
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return render_template_string(HTML_TEMPLATE, pdf_conversion_result=text)
        except ImportError:
            return render_template_string(HTML_TEMPLATE, error_message="PyMuPDF library not installed on server.")
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error_message=f"PDF conversion error: {e}")
        finally:
            os.remove(file_path) # Clean up uploaded file

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
=======
from flask import Flask, request, render_template_string, send_file
import os
import fitz # PyMuPDF library for PDF processing

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF to Text Converter</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
        .container { max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; background-color: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #007bff; text-align: center; margin-bottom: 25px; }
        h2 { color: #555; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-top: 30px; }
        input[type="file"] { margin-bottom: 15px; border: 1px solid #ddd; padding: 8px; border-radius: 4px; display: block; width: calc(100% - 20px); }
        button { padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background-color 0.3s ease; }
        button:hover { background-color: #218838; }
        textarea { width: 100%; height: 250px; margin-top: 20px; padding: 15px; border-radius: 6px; border: 1px solid #bbb; resize: vertical; font-size: 14px; line-height: 1.6; background-color: #f9f9f9; }
        .result { margin-top: 25px; padding: 15px; background-color: #e9f7ef; border: 1px solid #d4edda; border-radius: 6px; }
        .error { margin-top: 25px; padding: 15px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 6px; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF to Text Converter</h1>

        <h2>Convert PDF to TXT</h2>
        <form method="post" enctype="multipart/form-data" action="/pdf-to-txt">
            <input type="file" name="pdf_file" accept=".pdf" required>
            <button type="submit">Convert PDF to Text</button>
        </form>

        {% if pdf_conversion_result %}
        <div class="result">
            <h3>Extracted Text:</h3>
            <textarea readonly>{{ pdf_conversion_result }}</textarea>
        </div>
        {% endif %}

        {% if error_message %}
        <div class="error">
            <h3>Error:</h3>
            <p>{{ error_message }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Renders the main page with the PDF conversion form."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/pdf-to-txt', methods=['POST'])
def pdf_to_txt():
    """Handles PDF file upload and converts it to text."""
    # Check if a file was uploaded
    if 'pdf_file' not in request.files:
        return render_template_string(HTML_TEMPLATE, error_message="No PDF file part in the request.")
    
    file = request.files['pdf_file']

    # Check if the file input is empty
    if file.filename == '':
        return render_template_string(HTML_TEMPLATE, error_message="No selected PDF file.")
    
    # Check if the file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return render_template_string(HTML_TEMPLATE, error_message="Invalid file type. Please upload a PDF file.")

    # Process the uploaded file
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        try:
            file.save(file_path) # Save the uploaded file temporarily

            # Open the PDF and extract text using PyMuPDF (fitz)
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text() # Extract text from each page
            doc.close() # Close the document

            return render_template_string(HTML_TEMPLATE, pdf_conversion_result=text)
        except Exception as e:
            # Catch any errors during file saving or PDF processing
            return render_template_string(HTML_TEMPLATE, error_message=f"An error occurred during PDF processing: {e}. Please ensure it's a valid PDF.")
        finally:
            # Clean up the uploaded file from the server
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == '__main__':
    # This part runs only when you execute app.py directly for local testing
    # Render will use gunicorn to run the app in production
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
>>>>>>> 7c7bdb5dfa3717a7d188f5093bbabb694b7e64df
