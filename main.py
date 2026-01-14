import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

# --- DATABASE CONFIG ---
database_url = os.getenv("MYSQL_URL")

if database_url and database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODEL ---
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# --- CREATE TABLES ON STARTUP ---
with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Password check
    if password != confirm_password:
        flash("Passwords do not match!", "error")
        return redirect(url_for('index'))

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        flash("Email already registered!", "error")
        return redirect(url_for('index'))

    # Create new user
    new_user = User(
        first_name=firstname,
        last_name=lastname,
        email=email,
        password=password  # For production, hash passwords!
    )

    db.session.add(new_user)
    db.session.commit()

    return render_template('success.html')

@app.route('/users')
def view_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=users)

# --- RUN ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
