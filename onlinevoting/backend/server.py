from flask import Flask, request, jsonify
from models import db, User
from flask_mail import Mail, Message
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Enable CORS

# Database Configuration (Ensure it's set up correctly)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Change as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "nandamudiharika@gmail.com"  # Replace with your email
app.config['MAIL_PASSWORD'] = "usfrfxnxpwazlbqk"  # Use app-specific password

mail = Mail(app)
otp_store = {}

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({'success': False, 'message': 'All fields are required!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already exists!'}), 400

    new_user = User(email=email, username=username)
    new_user.set_password(password)  # Ensure this function exists in the User model
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'User registered successfully!'})

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return jsonify({'success': True, 'message': 'Login successful!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email")
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    try:
        msg = Message("Your OTP Code", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your OTP is {otp}"
        mail.send(msg)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email")
    user_otp = data.get("otp")

    if otp_store.get(email) == user_otp:
        del otp_store[email]
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/check-email', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'exists': True}), 200
    else:
        return jsonify({'exists': False}), 200
        
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure DB tables are created
    app.run(debug=True, port=5000)

