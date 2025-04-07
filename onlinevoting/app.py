from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User , Election, Candidate
from flask_mail import Mail, Message
from flask_cors import CORS
import random
from flask import Flask, render_template

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Configure Flask-Mail for OTP emails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "nandamudiharika@gmail.com"  # Replace with your email
app.config['MAIL_PASSWORD'] = "usfrfxnxpwazlbqk" # Use an app-specific password

mail = Mail(app)
otp_store = {}  # Temporary OTP storage

# ------------------------ AUTH ROUTES ------------------------

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email, username, password = data.get('email'), data.get('username'), data.get('password')

    if not email or not username or not password:
        return jsonify({'success': False, 'message': 'All fields are required!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already exists!'}), 400

    new_user = User(email=email, username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'User registered successfully!'})

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email, password = data.get('email'), data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return jsonify({'success': True, 'message': 'Login successful!'})
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
    email, user_otp = data.get("email"), data.get("otp")

    if otp_store.get(email) == user_otp:
        del otp_store[email]
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/check-email', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email')

    existing_user = User.query.filter_by(email=email).first()
    return jsonify({'exists': bool(existing_user)})

# ------------------------ ELECTION ROUTES ------------------------

@app.route('/api/elections')
def get_elections():
    elections = Election.query.all()
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'description': e.description,
        'image_url': e.image_url
    } for e in elections])

@app.route('/api/election/<int:election_id>')
def get_election_details(election_id):
    election = Election.query.get_or_404(election_id)
    candidates = Candidate.query.filter_by(election_id=election.id).all()
    return jsonify({
        'id': election.id,
        'title': election.title,
        'description': election.description,
        'image_url': election.image_url,
        'candidates': [{'id': c.id, 'name': c.name, 'party': c.party, 'votes': c.votes} for c in candidates]
    })

@app.route('/get_election_details', methods=['GET'])
def get_election_detailsv2():
    election_id = request.args.get("election_id")
    if not election_id:
        return jsonify({"success": False, "message": "Election ID is required"}), 400

    election = Election.query.filter_by(id=election_id).first()
    if not election:
        return jsonify({"success": False, "message": "Election not found"}), 404

    candidates = Candidate.query.filter_by(election_id=election_id).all()
    candidate_list = [
        {"id": c.id, "name": c.name, "party": c.party, "votes": c.votes}
        for c in candidates
    ]

    response = {
        "success": True,
        "title": election.title,
        "description": election.description,
        "image_url": election.image_url,
        "candidates": candidate_list
    }

    return jsonify(response)

@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    data = request.json
    candidate_id = data.get("candidate_id")

    if not candidate_id:
        return jsonify({"success": False, "message": "Candidate ID is required"}), 400

    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({"success": False, "message": "Candidate not found"}), 404

    candidate.votes += 1
    db.session.commit()

    return jsonify({"success": True, "message": "Vote cast successfully!","election_id":candidate.election_id})


# ------------------------ DATABASE INIT ------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    #app.run(debug=True, port=5000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
