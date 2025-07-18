from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Setup folders and database
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create uploads folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Report model
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)

# Create DB
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    reports = Report.query.order_by(Report.id.desc()).all()
    return render_template('home.html', reports=reports)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        location = request.form['location']
        contact = request.form['contact']
        date = request.form['date']
        image = request.files['image']

        filename = None
        if image and image.filename != '':
            if image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Only image files are allowed!", "danger")
                return redirect(url_for('submit'))

        report = Report(category=category, description=description,
                        location=location, contact=contact,
                        date=date, image_filename=filename)

        db.session.add(report)
        db.session.commit()
        flash("Report submitted successfully!", "success")
        return redirect(url_for('home'))

    return render_template('submit.html')

@app.route('/delete/<int:report_id>')
def delete(report_id):
    report = Report.query.get_or_404(report_id)
    if report.image_filename:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], report.image_filename)
        if os.path.exists(img_path):
            os.remove(img_path)
    db.session.delete(report)
    db.session.commit()
    flash("Report deleted successfully.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
