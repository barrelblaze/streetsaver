from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secretkey'

# Image upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Report model
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(100))

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Report form page
@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        location = request.form['location']
        image = request.files.get('image')

        image_filename = None
        if image and image.filename:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        new_report = Report(
            category=category,
            description=description,
            location=location,
            image_filename=image_filename
        )

        db.session.add(new_report)
        db.session.commit()
        flash('Report submitted successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('report.html')

# Display all reports
@app.route('/reports')
def reports():
    reports = Report.query.all()
    return render_template('reports.html', reports=reports)

# Create database tables before starting the app
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
