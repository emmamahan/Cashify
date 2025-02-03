from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import hashlib
import sqlite3
import secrets
import pytesseract
from PIL import Image
import io

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/cashify"

INITIAL_BUDGET = 500

# Database setup
def init_db():
    conn = sqlite3.connect('cashify.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  budget REAL DEFAULT 500.0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS receipts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  date TEXT,
                  total REAL,
                  image_path TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  receipt_id INTEGER,
                  name TEXT,
                  price REAL,
                  category TEXT,
                  FOREIGN KEY (receipt_id) REFERENCES receipts(id))''')
    conn.commit()
    conn.close()

init_db()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Set the path to your Tesseract executable if needed
# For example, on Windows, you may need to set this path:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
mail = Mail(app)

# Route for scanning receipt
@app.route('/scan-receipt', methods=['POST'])
def scan_receipt():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    img = Image.open(io.BytesIO(file.read()))

    text = pytesseract.image_to_string(img)
    purchases = extract_purchases(text)

    return jsonify({"purchases": purchases})

@app.route('/upload_receipt', methods=['POST'])
def upload_receipt():
    user_id = request.form['user_id']
    date = request.form['date']
    total = request.form['total']
    file = request.files['receipt']
    
    if file:
        filename = f"{user_id}_{date}_{file.filename}"
        file.save(os.path.join('uploads', filename))
        
        conn = sqlite3.connect('cashify.db')
        c = conn.cursor()
        c.execute("INSERT INTO receipts (user_id, date, total, image_path) VALUES (?, ?, ?, ?)",
                  (user_id, date, total, filename))
        receipt_id = c.lastrowid
        
        # Here you would process the receipt image and extract items
        # For demonstration, we'll add dummy items
        items = [
            ("Apples", 5.99, "Groceries"),
            ("Milk", 3.49, "Groceries"),
            ("Movie Ticket", 12.99, "Entertainment")
        ]
        
        for item in items:
            c.execute("INSERT INTO items (receipt_id, name, price, category) VALUES (?, ?, ?, ?)",
                      (receipt_id, item[0], item[1], item[2]))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Receipt uploaded successfully"}), 200
    else:
        return jsonify({"error": "No file uploaded"}), 400
    
@app.route('/submit-purchases', methods=['POST'])
def submit_purchases():
    purchases = request.json['purchases']
    user_id = "dummy_user_id"  # In a real app, you'd get this from the session

    # Update user's budget and purchases in the database
    user = mongo.db.users.find_one_and_update(
        {"_id": user_id},
        {
            "$push": {"purchases": {"$each": purchases}},
            "$inc": {"budget": -sum(purchase['amount'] for purchase in purchases)}
        },
        return_document=True
    )

    if not user:
        # If user doesn't exist, create a new one
        user = {
            "_id": user_id,
            "budget": INITIAL_BUDGET - sum(purchase['amount'] for purchase in purchases),
            "purchases": purchases
        }
        mongo.db.users.insert_one(user)

    category_distribution = calculate_category_distribution(user['purchases'])

    return jsonify({
        "remainingBudget": user['budget'],
        "categoryDistribution": category_distribution
    })

def extract_purchases(text):
    # Implement your logic to extract purchases from the OCR text
    # This is a placeholder implementation
    return [
        {"category": "Food", "amount": 100.0},
        {"category": "Entertainment", "amount": 50.0},
        {"category": "Shopping", "amount": 200.0},
    ]

def calculate_category_distribution(purchases):
    categories = {}
    for purchase in purchases:
        if purchase['category'] not in categories:
            categories[purchase['category']] = 0
        categories[purchase['category']] += purchase['amount']
    
    total = sum(categories.values())
    return {category: (amount / total) * 100 for category, amount in categories.items()}






@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin')
def login_page():
    return render_template('login.html')

@app.route('/settings', methods=['GET', 'POST'])
def get_settings():

    pass
@app.route('/logout', methods=['GET', 'POST'])
def get_logout():
    pass

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json['email']
    # Generate a unique token
    token = secrets.token_urlsafe(32)
    # TODO: Save the token in your database, associated with the user's email

    # Send reset email
    msg = Message('Password Reset Request',
                  sender='noreply@example.com',
                  recipients=[email])
    msg.body = f'Click the following link to reset your password: http://yourdomain.com/reset-password/{token}'
    mail.send(msg)

    return jsonify({'message': 'Password reset link sent to your email'}), 200

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    password = hash_password(data['password'])
    
    conn = sqlite3.connect('cashify.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = hash_password(data['password'])
    
    conn = sqlite3.connect('cashify.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({"message": "Login successful", "user_id": user[0]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


if __name__ == '__main__':
    app.run(debug=True)