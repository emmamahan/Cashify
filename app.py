from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
import io

app = Flask(__name__)

# Set the path to your Tesseract executable if needed
# For example, on Windows, you may need to set this path:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


@app.route('/')
def index():
    return render_template('index.html')


# Route for scanning receipt
@app.route('/scan-receipt', methods=['POST'])
def scan_receipt():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    img = Image.open(io.BytesIO(file.read()))

    # Use Tesseract OCR to extract text from the image
    text = pytesseract.image_to_string(img)

    # Process the extracted text into structured data (dummy implementation)
    purchases = extract_purchases(text)

    # Respond with the categorized purchases
    return jsonify({"purchases": purchases})


# Function to extract purchases (dummy for now)
def extract_purchases(text):
    # Dummy data for testing purposes
    # Here, you'd parse the `text` variable to extract categories and amounts
    return [
        {"category": "Food", "amount": 100.0},
        {"category": "Entertainment", "amount": 50.0},
        {"category": "Shopping", "amount": 200.0},
    ]


if __name__ == '__main__':
    app.run(debug=True)