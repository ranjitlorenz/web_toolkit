from flask import Flask, request, render_template_string
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
    <title>PDF to Plain Text Converter</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f4f4f4; 
            color: #333; 
        }
        .container { 
            max-width: 600px; /* Adjusted max-width for better fit */
            margin: auto; 
            padding: 20px; 
            border: 1px solid #ccc; 
            border-radius: 8px; 
            background-color: #fff; 
            box-shadow: 0 0 10px rgba(0,0,0,0.1); 
        }
        h1 { 
            color: #007bff; 
            text-align: center; 
            margin-bottom: 25px; 
        }
        h2 { 
            color: #555; 
            border-bottom: 1px solid #eee; 
            padding-bottom: 10px; 
            margin-top: 30px; 
        }
        input[type="file"] { 
            margin-bottom: 15px; 
            border: 1px solid #ddd; 
            padding: 8px; 
            border-radius: 4px; 
            display: block; 
            width: calc(100% - 20px); 
        }
        button { 
            padding: 10px 20px; 
            background-color: #28a745; 
            color: white; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
            transition: background-color 0.3s ease; 
        }
        button:hover { 
            background-color: #218838; 
        }
        
        /* Styles for the extracted text display (now a textarea) */
        textarea.extracted-text-display {
            width: 100%;
            height: 400px; /* Increased height for better viewing */
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #bbb;
            resize: vertical; /* Allow user to resize textarea */
            font-size: 14px;
            line-height: 1.6;
            background-color: #f9f9f9;
            /* Generic font stack for broad Unicode support */
            font-family: "Segoe UI", "Roboto", "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
            white-space: pre-wrap; /* Preserve whitespace and line breaks */
            word-wrap: break-word; /* Break long words */
        }

        .result { 
            margin-top: 25px; 
            padding: 15px; 
            background-color: #e9f7ef; 
            border: 1px solid #d4edda; 
            border-radius: 6px; 
        }
        .error { 
            margin-top: 25px; 
            padding: 15px; 
            background-color: #f8d7da; 
            border: 1px solid #f5c6cb; 
            border-radius: 6px; 
            color: #721c24; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF to Plain Text Converter</h1>

        <h2>Convert PDF to TXT</h2>
        <form method="post" enctype="multipart/form-data" action="/pdf-to-txt">
            <input type="file" name="pdf_file" accept=".pdf" required>
            <button type="submit">Convert PDF to Text</button>
        </form>

        {% if pdf_conversion_result %}
        <div class="result">
            <h3>Extracted Text:</h3>
            {# Display plain text in a textarea #}
            <textarea class="extracted-text-display" readonly>{{ pdf_conversion_result }}</textarea>
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
    """Handles PDF file upload and converts it to plain text."""
    if 'pdf_file' not in request.files:
        return render_template_string(HTML_TEMPLATE, error_message="No PDF file part in the request.")
    
    file = request.files['pdf_file']
    if file.filename == '':
        return render_template_string(HTML_TEMPLATE, error_message="No selected PDF file.")
    if not file.filename.lower().endswith('.pdf'):
        return render_template_string(HTML_TEMPLATE, error_message="Invalid file type. Please upload a PDF file.")

    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        try:
            file.save(file_path) # Save the uploaded file temporarily

            doc = fitz.open(file_path)
            plain_text = ""
            for page in doc:
                # Revert to get_text() for plain text extraction
                plain_text += page.get_text() 
            doc.close() # Close the document

            return render_template_string(HTML_TEMPLATE, pdf_conversion_result=plain_text)
        except Exception as e:
            # Catch any errors during file saving or PDF processing
            return render_template_string(HTML_TEMPLATE, error_message=f"An error occurred during PDF processing: {e}. Please ensure it's a valid PDF with a text layer.")
        finally:
            # Clean up the uploaded file from the server
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == '__main__':
    # This part runs only when you execute app.py directly for local testing
    # Render will use gunicorn to run the app in production
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))