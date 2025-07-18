from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streetsaver.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# ===================== MODELS =====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    contact = db.Column(db.String(20))
    date = db.Column(db.String(50))
    image = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# ===================== ROUTES =====================

@app.route('/')
def index():
    if 'user_id' in session:
        reports = Report.query.all()
        return render_template('home.html', reports=reports, logged_in=True)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash("Username already exists", "danger")
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(username=request.form['username'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['image']
        filename = None
        if file and file.filename != '':
            filename = datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        report = Report(
            category=request.form['category'],
            description=request.form['description'],
            location=request.form['location'],
            contact=request.form['contact'],
            date=request.form['date'],
            image=filename,
            user_id=session['user_id']
        )
        db.session.add(report)
        db.session.commit()
        flash("Report submitted successfully!", "success")
        return redirect(url_for('index'))
    return render_template('submit.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    report = Report.query.get_or_404(id)
    if report.user_id == session['user_id']:
        db.session.delete(report)
        db.session.commit()
        flash("Report deleted successfully.", "info")
    else:
        flash("Unauthorized delete attempt.", "danger")
    return redirect(url_for('index'))

# ===================== DB INIT =====================

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
