from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Route to redirect for login

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # is_active column to control user activity

    def __init__(self, user_name, email, password, category, is_active=True):
        self.user_name = user_name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.category = category
        self.is_active = is_active

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def is_active(self):
        return self.is_active  # Flask-Login checks this by default

# Initialize database
with app.app_context():
    db.create_all()

# Load user for login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes

@app.route('/')
def index():
    return render_template('main.html')  # Main page with options (Admin, User, Vendor)

@app.route('/signup/<role>', methods=['GET', 'POST'])
def signup(role):
    if request.method == 'POST':
        user_name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        category = request.form['category']

        # Check if passwords match
        if password != confirm_password:
            return render_template('signup.html', role=role, error="Passwords do not match.")

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('signup.html', role=role, error="Email already registered.")
        
        # Create new user and add to the database
        new_user = User(user_name=user_name, email=email, password=password, category=category)
        db.session.add(new_user)
        db.session.commit()

        # Redirect to login page after successful signup
        return redirect(url_for('login', role=role))  

    return render_template('signup.html', role=role)

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(user_name=username).first()
        if user and user.check_password(password):
            login_user(user)  # Log the user in
            return redirect(url_for('dashboard', role=role))
        else:
            return render_template('login.html', role=role, error="Invalid credentials.")
    
    return render_template('login.html', role=role)

@app.route('/dashboard/<role>')
@login_required
def dashboard(role):
    if current_user.category == 'admin':
        return render_template('admin_dashboard.html')
    elif current_user.category == 'user':
        return render_template('user_dashboard.html')
    else:
        return render_template('vendor_dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', role=current_user.category))

if __name__ == '__main__':
    app.run(debug=True)
