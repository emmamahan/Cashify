from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import hashlib
import sqlite3
import secrets
import pytesseract
from PIL import Image
import io
import re

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/cashify"

INITIAL_BUDGET = 500

# Database setup
# def init_db():
#     conn = sqlite3.connect('cashify.db')
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS users
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   username TEXT UNIQUE NOT NULL,
#                   password TEXT NOT NULL,
#                   budget REAL DEFAULT 500.0)''')
#     c.execute('''CREATE TABLE IF NOT EXISTS receipts
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   user_id INTEGER,
#                   date TEXT,
#                   total REAL,
#                   image_path TEXT,
#                   FOREIGN KEY (user_id) REFERENCES users(id))''')
#     c.execute('''CREATE TABLE IF NOT EXISTS items
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   receipt_id INTEGER,
#                   name TEXT,
#                   price REAL,
#                   category TEXT,
#                   FOREIGN KEY (receipt_id) REFERENCES receipts(id))''')
#     conn.commit()
#     conn.close()

# init_db()

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
    #print(text)
    purchases = extract_items_from_receipt(text)

    return jsonify({"purchases": purchases})

def extract_items_from_receipt(text):
    # Perform OCR on the image
    # Process the extracted text to find items and prices
    items = []
    lines = text.split('\n')
    for line in lines:
        # Use regex to find item name and price
        if "$" in line and "total" not in line.lower():
            
            name = re.sub(r'[^\w\s]|[\d]', '', line.split("$")[0].lower()).strip()
            category = categorize_item(name)
            price = line.split("$")[1].lower().strip()
            try: price = float(price)
            except: 
                print(f"FAIL: {price}")
                price = 0
            print(name)
            print(price)
            items.append({"name": name, "price": price, "category": category})
    
    return items

def categorize_item(name):
    # This is a simple categorization function. You can expand it with more categories and items.
    name = name.lower()
    if any(food in name for food in [
    "milk", "bread", "eggs", "cheese", "yogurt", "butter",
    "apples", "bananas", "oranges", "tomatoes", "lettuce", "carrots",
    "potatoes", "onions", "chicken", "ground beef", "pasta", "rice",
    "cereal", "coffee", "tea", "sugar", "flour", "salt", "pepper",
    "olive oil", "ketchup", "mustard", "mayonnaise", "peanut butter",
    "jelly", "jam", "soup", "canned vegetables", "canned fruits",
    "frozen pizza", "ice cream", "chips", "cookies", "soda", "juice",
    "bacon", "sausage", "ham", "tuna", "salmon", "cajun shrimp",
    "broccoli", "cauliflower", "spinach", "cucumber", "bell peppers",
    "mushrooms", "garlic", "ginger", "lemons", "limes", "avocados",
    "berries", "grapes", "melons", "pineapple", "nuts", "dried fruits",
    "honey", "syrup", "salsa", "hummus", "guacamole", "tortillas",
    "bagels", "muffins", "crackers", "oatmeal", "pancake mix",
    "chocolate", "candy", "popcorn", "pretzels", "granola bars, burger, drinks", 
    "cajun shrine", "iepossible burser", "soft drinks", "ribeye cheesesteak foo roll" # this is temporary
    ]):
        return 'Food'
    elif any(household in name for household in [
    "screws", "nails", "wall anchors", "wood glue", "duct tape", "super glue",
    "sandpaper", "paint", "paint brushes", "paint rollers", "drop cloth",
    "caulk", "caulking gun", "plumbing tape", "PVC pipe", "pipe wrench",
    "hammer", "screwdriver", "drill bits", "measuring tape", "level",
    "utility knife", "putty knife", "spackle", "electrical tape", "light bulbs",
    "extension cords", "outlet covers", "door hinges", "cabinet knobs",
    "brackets", "hooks", "wood stain", "varnish", "sealant", "tiles",
    "grout", "adhesive", "floor protectors", "all-purpose cleaner", 
    "glass cleaner", "disinfectant wipes", "bleach", "laundry detergent", 
    "fabric softener", "dryer sheets", "stain remover", "dish soap", 
    "sponges", "scrub brushes", "mop", "broom", "dustpan", "vacuum bags",
    "garbage bags", "paper towels", "microfiber cloths", "toilet cleaner",
    "drain cleaner", "air freshener", "oven cleaner", "stainless steel cleaner",
    "wood polish", "carpet cleaner", "rubber gloves", "bucket"]):
        return 'Household'
    elif any(clothing in name for clothing in [
    "t-shirt", "shirt", "blouse", "sweater", "cardigan", "hoodie",
    "jacket", "coat", "blazer", "jeans", "pants", "trousers", "shorts",
    "skirt", "dress", "suit", "socks", "underwear", "bra", "undershirt",
    "pajamas", "nightgown", "robe", "slippers", "shoes", "sneakers",
    "boots", "sandals", "flip-flops", "heels", "flats", "loafers",
    "belt", "tie", "scarf", "gloves", "mittens", "hat", "cap", "beanie",
    "swimsuit", "bikini", "trunks", "leggings", "tights", "stockings",
    "vest", "tank top", "polo shirt", "sweatshirt", "sweatpants",
    "raincoat", "windbreaker", "parka", "overalls", "jumpsuit",
    "uniform", "apron", "bow tie", "cummerbund", "camisole",
    "lingerie", "boxers", "briefs", "pantyhose", "knee-highs",
    "ankle socks", "crew socks", "dress shirt", "tunic", "poncho",
    "shawl", "wrap", "cardigan", "bolero", "crop top", "halter top",
    "turtleneck", "v-neck", "crew neck", "collared shirt"]):
        return 'Clothing'
    elif any(healthBeauty in name for healthBeauty in [
    "shampoo", "conditioner", "body wash", "soap", "face wash", "moisturizer",
    "lotion", "sunscreen", "deodorant", "antiperspirant", "perfume", "cologne",
    "toothpaste", "toothbrush", "mouthwash", "dental floss", "lip balm",
    "lipstick", "mascara", "eyeliner", "eyeshadow", "blush", "foundation",
    "concealer", "powder", "bronzer", "highlighter", "makeup remover",
    "nail polish", "nail polish remover", "cotton swabs", "cotton balls",
    "hair gel", "hair spray", "hair dye", "hair brush", "comb", "hair ties",
    "bobby pins", "razor", "shaving cream", "aftershave", "wax strips",
    "tweezers", "scissors", "nail clippers", "emery board", "face mask",
    "eye cream", "hand cream", "foot cream", "body scrub", "face scrub",
    "toner", "serum", "acne treatment", "hand sanitizer", "bandages",
    "first aid kit", "pain reliever", "antacid", "allergy medicine",
    "vitamins", "supplements", "protein powder", "feminine hygiene products",
    "condoms", "contact lens solution", "eye drops", "facial tissues",
    "body spray", "dry shampoo", "face wipes", "body lotion", "hand soap",
    "shaving gel", "beard oil", "hair mask", "face peel", "exfoliator",
    "bath bombs", "bubble bath", "shower gel", "body mist", "face primer",
    "setting spray", "brow pencil", "hair removal cream", "sunless tanner"]):
        return 'Health & Beauty'
    elif any(entertainment in name for entertainment in[
    "movie ticket", "concert ticket", "theater ticket", "museum admission",
    "amusement park pass", "zoo ticket", "aquarium ticket", "festival pass",
    "book", "magazine", "newspaper", "comic book", "e-book",
    "dvd", "blu-ray", "video game", "video game console", "board game",
    "puzzle", "playing cards", "toy", "action figure", "doll",
    "lego set", "model kit", "art supplies", "coloring book",
    "musical instrument", "guitar strings", "sheet music",
    "streaming service subscription", "music download",
    "movie rental", "popcorn", "candy", "soda", "nachos",
    "sports equipment", "gym membership", "fitness class",
    "bowling", "mini golf", "laser tag", "escape room",
    "karaoke", "arcade tokens", "casino chips",
    "lottery ticket", "scratch card", "bingo supplies",
    "party supplies", "balloons", "decorations",
    "costume", "face paint", "photo booth rental",
    "camera", "camera accessories", "binoculars",
    "camping gear", "fishing equipment", "hiking gear",
    "beach toys", "pool float", "inflatable boat",
    "sports jersey", "team merchandise", "souvenir",
    "travel guide", "map", "language learning software",
    "cooking class", "dance class", "art class",
    "craft kit", "scrapbooking supplies", "knitting supplies",
    "gardening tools", "plant", "seed packet",
    "pet toy", "aquarium supplies", "bird feeder"]):
        return 'Entertainment'
    elif any(AE in name for AE in[
    "smartphone", "tablet", "laptop", "desktop computer", "monitor",
    "printer", "scanner", "keyboard", "mouse", "speakers",
    "headphones", "earbuds", "smart watch", "fitness tracker",
    "television", "smart TV", "streaming device", "DVD player", "Blu-ray player",
    "gaming console", "virtual reality headset", "camera", "camcorder",
    "microphone", "router", "modem", "external hard drive", "USB drive",
    "memory card", "power bank", "charger", "cable", "adapter",
    "refrigerator", "freezer", "dishwasher", "washing machine", "dryer",
    "oven", "stove", "microwave", "toaster", "toaster oven",
    "coffee maker", "espresso machine", "blender", "food processor",
    "stand mixer", "hand mixer", "slow cooker", "pressure cooker",
    "air fryer", "rice cooker", "electric kettle", "waffle maker",
    "vacuum cleaner", "robot vacuum", "steam mop", "iron",
    "hair dryer", "straightener", "curling iron", "electric shaver",
    "electric toothbrush", "air purifier", "humidifier", "dehumidifier",
    "fan", "space heater", "air conditioner", "thermostat",
    "smart speaker", "smart home hub", "security camera", "doorbell camera",
    "smoke detector", "carbon monoxide detector", "light bulb", "smart light",
    "electric blanket", "heated mattress pad", "white noise machine",
    "clock radio", "calculator", "label maker", "paper shredder"]):
        return 'A&E'
    elif "tax" in name:
        return "Tax"
    else:
        return 'Miscellaneous'

@app.route('/submit-purchases', methods=['POST'])
def submit_purchases():
    purchases = request.json['purchases']
    user_id = request.json['user_id']
    
    conn = sqlite3.connect('cashify.db')
    c = conn.cursor()
    
    try:
        # Get current budget
        c.execute("SELECT budget FROM users WHERE user_id = ?", (user_id,))
        current_budget = c.fetchone()[0]
        
        # Calculate total spent
        total_spent = sum(purchase['amount'] for purchase in purchases)
        
        # Update budget
        new_budget = current_budget - total_spent
        c.execute("UPDATE users SET budget = ? WHERE user_id = ?", (new_budget, user_id))
        
        # Insert purchases
        for purchase in purchases:
            c.execute("INSERT INTO items (user_id, name, price, category) VALUES (?, ?, ?, ?)",
                      (user_id, purchase['name'], purchase['amount'], purchase['category']))
        
        conn.commit()
        
        category_distribution = calculate_category_distribution(purchases)
        
        return jsonify({
            "remainingBudget": new_budget,
            "categoryDistribution": category_distribution
        })
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


def calculate_category_distribution(purchases):
    categories = {}
    for purchase in purchases:
        if purchase['category'] not in categories:
            categories[purchase['category']] = 0
        categories[purchase['category']] += purchase['amount']
    
    total = sum(categories.values())
    return {category: (amount / total) * 100 for category, amount in categories.items()}



@app.route('/get_budget', methods=['POST'])
def get_budget():
    data = request.json
    user_id = data['user_id']
    
    conn = sqlite3.connect('cashify.db')
    c = conn.cursor()
    try:
        print(user_id)
        c.execute("SELECT budget FROM users WHERE user_id = ?", (user_id, ))
        current_budget = c.fetchone()[0]
        return jsonify({"curr_budget": current_budget}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

    

@app.route('/update-budget', methods=['POST'])
def update_budget():
    data = request.json
    print(data)
    user_id = 1

    if "purchases" in data:
        user_id = data['user_id']
        purchases = data['purchases']
        
    
        total_price = 0
        for purchase in purchases:
            total_price += purchase['price']
    
        conn = sqlite3.connect('cashify.db')
        c = conn.cursor()
        try:
            c.execute("SELECT budget FROM users WHERE user_id = ?", (user_id,))
            curr_budget = c.fetchone()[0]
            new_budget = round(curr_budget - total_price, 2)
            print("DONE")
            c.execute("UPDATE users SET budget = ? WHERE user_id = ?", (new_budget, user_id))
            conn.commit()
            return jsonify({"message": "Budget updated successfully", "new_budget": new_budget}), 200
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            conn.close()

    else:
        budget = data["budget"]

        conn = sqlite3.connect('cashify.db')
        c = conn.cursor()
        try:
            c.execute("UPDATE users SET budget = ? WHERE user_id = ?", (budget, user_id))
            conn.commit()
            return jsonify({"message": "Budget updated successfully", "new_budget": budget}), 200
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 400
        finally:
            conn.close()




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


# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.json
#     username = data['username']
#     password = hash_password(data['password'])
    
#     conn = sqlite3.connect('cashify.db')
#     c = conn.cursor()
#     try:
#         c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
#         conn.commit()
#         return jsonify({"message": "User registered successfully"}), 201
#     except sqlite3.IntegrityError:
#         return jsonify({"error": "Username already exists"}), 400
#     finally:
#         conn.close()
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     username = data['username']
#     password = hash_password(data['password'])
    
#     conn = sqlite3.connect('cashify.db')
#     c = conn.cursor()
#     c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
#     user = c.fetchone()
#     conn.close()
    
#     if user:
#         return jsonify({"message": "Login successful", "user_id": user[0]}), 200
#     else:
#         return jsonify({"error": "Invalid credentials"}), 401


if __name__ == '__main__':
    app.run(debug=True)