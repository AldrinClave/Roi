import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

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
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- CREATE TABLES ON STARTUP (Gunicorn safe) ---
with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    new_user = User(
        first_name=request.form.get('firstname'),
        last_name=request.form.get('lastname'),
        email=request.form.get('email'),
        password=request.form.get('password')
    )

    db.session.add(new_user)
    db.session.commit()

    return render_template('success.html')

@app.route('/users')
def view_users():
    users = User.query.all()
    return render_template('users.html', users=users)

# --- RUN ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
