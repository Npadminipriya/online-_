from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting.db'

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    votes = db.relationship('Vote', backref='voter', lazy=True)

class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    candidates = db.relationship('Candidate', backref='election', lazy=True)
    votes = db.relationship('Vote', backref='election', lazy=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    votes = db.relationship('Vote', backref='candidate', lazy=True)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)

# Function to create sample elections
def create_sample_elections():
    if Election.query.first():
        return

    elections = [
        {
            'title': 'Class Representative Election',
            'description': 'Election for selecting class representative for 2024',
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=7),
            'candidates': [
                {'name': 'John Doe', 'description': 'Senior student with leadership experience'},
                {'name': 'Jane Smith', 'description': 'Active member of student council'}
            ]
        },
        {
            'title': 'Student Council President',
            'description': 'Election for Student Council President position',
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=5),
            'candidates': [
                {'name': 'Mike Johnson', 'description': 'Previous vice president'},
                {'name': 'Sarah Williams', 'description': 'Head of debate club'}
            ]
        }
    ]

    for election_data in elections:
        election = Election(
            title=election_data['title'],
            description=election_data['description'],
            start_date=election_data['start_date'],
            end_date=election_data['end_date'],
            is_active=True
        )
        db.session.add(election)
        db.session.flush()

        for candidate_data in election_data['candidates']:
            candidate = Candidate(
                name=candidate_data['name'],
                description=candidate_data['description'],
                election_id=election.id
            )
            db.session.add(candidate)

    db.session.commit()

# Routes
@app.route('/')
def index():
    elections = Election.query.filter_by(is_active=True).all()
    return render_template('index.html', elections=elections)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in successfully')
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully')
    return redirect(url_for('index'))

@app.route('/election/<int:election_id>')
def election_detail(election_id):
    election = Election.query.get_or_404(election_id)
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    return render_template('election_detail.html', election=election, candidates=candidates)

@app.route('/vote/<int:election_id>', methods=['POST'])
def vote(election_id):
    if 'user_id' not in session:
        flash('Please login to vote')
        return redirect(url_for('login'))

    election = Election.query.get_or_404(election_id)
    candidate_id = request.form.get('candidate_id')

    if not election.is_active:
        flash('This election is closed')
        return redirect(url_for('election_detail', election_id=election_id))

    existing_vote = Vote.query.filter_by(user_id=session['user_id'], election_id=election_id).first()

    if existing_vote:
        flash('You have already voted in this election')
        return redirect(url_for('election_detail', election_id=election_id))

    vote = Vote(
        user_id=session['user_id'],
        election_id=election_id,
        candidate_id=candidate_id
    )
    db.session.add(vote)
    db.session.commit()
    flash('Vote recorded successfully')
    return redirect(url_for('election_detail', election_id=election_id))

# Admin functions
def is_admin():
    if 'user_id' not in session:
        return False
    user = User.query.get(session['user_id'])
    return user and user.is_admin

# Running the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_elections()
    app.run(debug=True)
