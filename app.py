import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

# 1. INITIALISATION
app = Flask(__name__)

# 2. CONFIGURATION
app.config['SECRET_KEY'] = 'streamdeck-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 3. MODÈLES
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100), unique=True)
    is_admin = db.Column(db.Boolean, default=False)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    category = db.Column(db.String(50))
    season = db.Column(db.String(50), nullable=True)
    poster_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 4. ROUTES
@app.route('/')
@login_required
def index():
    search = request.args.get('search')
    if search:
        items = Content.query.filter(Content.title.contains(search)).all()
    else:
        items = Content.query.all()
    return render_template('index.html', items=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pwd = request.form.get('password')
        user = User.query.filter_by(password=pwd).first()
        if user:
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    if request.method == 'POST':
        new_item = Content(
            title=request.form['title'],
            category=request.form['category'],
            season=request.form.get('season'),
            poster_url=request.form['poster'],
            video_url=request.form['video']
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('admin'))
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin.html', users=users)

@app.route('/generate_user')
@login_required
def generate_user():
    if not current_user.is_admin: return redirect(url_for('index'))
    new_code = str(uuid.uuid4())[:6].upper()
    db.session.add(User(password=new_code))
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin: return redirect(url_for('index'))
    u = User.query.get(user_id)
    if u:
        db.session.delete(u)
        db.session.commit()
    return redirect(url_for('admin'))

# 5. DÉMARRAGE
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(is_admin=True).first():
            db.session.add(User(password='ADMIN123', is_admin=True))
            db.session.commit()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
