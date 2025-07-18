from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reports.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    reports = Report.query.order_by(Report.id.desc()).all()
    return render_template('home.html', reports=reports)

@app.route('/report', methods=['POST'])
def report():
    category = request.form['category']
    description = request.form['description']
    location = request.form['location']
    image = request.files['image']

    filename = None
    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_report = Report(
        category=category,
        description=description,
        location=location,
        image_filename=filename
    )
    db.session.add(new_report)
    db.session.commit()
    flash("Report submitted successfully.")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
