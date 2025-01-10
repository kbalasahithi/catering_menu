from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catering.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role='customer')
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    items = MenuItem.query.all()
    return render_template('menu.html', items=items)

@app.route('/admin')
@login_required
def admin():
    if not current_user.role == 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    items = MenuItem.query.all()
    return render_template('admin.html', items=items)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('index'))

def init_db():
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
def init_menu_items():
    with app.app_context():
        # Only add items if menu is empty
        if MenuItem.query.count() == 0:
            menu_items = [
                # Appetizers
                MenuItem(
                    name="Chicken 65",
                    description="Spicy, deep-fried chicken marinated in authentic Indian spices, served with mint chutney",
                    price=12.99,
                    category="Appetizers"
                ),
                MenuItem(
                    name="Goat Fry",
                    description="Tender pieces of goat marinated and fried with aromatic Indian spices",
                    price=15.99,
                    category="Appetizers"
                ),
                
                # Main Course
                MenuItem(
                    name="Special Biryani",
                    description="Fragrant basmati rice cooked with tender meat, aromatic spices, and fresh herbs",
                    price=18.99,
                    category="Main Course"
                ),
                MenuItem(
                    name="Traditional Thali",
                    description="Complete Indian meal with rice, dal, curry, vegetables, roti, and accompaniments",
                    price=16.99,
                    category="Main Course"
                ),
                
                # Desserts
                MenuItem(
                    name="Gulab Jamun",
                    description="Soft milk-solid dumplings soaked in rose and cardamom flavored sugar syrup",
                    price=6.99,
                    category="Desserts"
                ),
                MenuItem(
                    name="Special Ice Cream",
                    description="Choice of Indian flavors including mango, pistachio, and saffron",
                    price=5.99,
                    category="Desserts"
                )
            ]
            
            for item in menu_items:
                db.session.add(item)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    init_menu_items() 
    app.run(debug=True)
