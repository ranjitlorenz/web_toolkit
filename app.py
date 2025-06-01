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