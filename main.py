from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Secret key for flash messages
app.secret_key = 'nuezca'

# MySQL Database Configuration
# Format: mysql+pymysql://username:password@host/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/registration'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define User Model (represents the 'users' table)
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<User {self.email}>'

# Route: Registration Form
@app.route('/')
def home():
    return render_template('register.html')

# Route: Handle Registration
@app.route('/register', methods=['POST'])
def register():
    # Get form data
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Simple validation
    if password != confirm_password:
        flash('Passwords do not match!', 'error')
        return redirect(url_for('home'))

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already registered!', 'error')
        return redirect(url_for('home'))

    # Create new user
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password  # In production, hash this!
    )

    # Save to database
    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('success'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('home'))

# Route: Success Page
@app.route('/success')
def success():
    return render_template('success.html')

# Route: View All Users (for demonstration)
@app.route('/users')
def view_users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

if __name__ == '__main__':
    app.run(debug=True)