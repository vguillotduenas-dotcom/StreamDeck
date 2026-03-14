import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ma-super-cle-secrete'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODÈLES ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    code = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(20), default='user') # 'admin' ou 'user'

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    img = db.Column(db.String(500))
    lien = db.Column(db.String(500))

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

# --- INITIALISATION ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(nom="Admin", prenom="Principal", code='ADMIN123', role='admin')
        db.session.add(admin)
        db.session.commit()

# --- ROUTES ---

@app.route('/')
@login_required
def index():
    tous_les_films = Video.query.all()
    return render_template('index.html', films=tous_les_films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code_saisi = request.form.get('code')
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        
        user = User.query.filter_by(code=code_saisi).first()
        
        if user:
            # Si c'est un nouvel utilisateur (pas encore de nom enregistré)
            if user.role == 'user' and not user.nom:
                user.nom = nom
                user.prenom = prenom
                db.session.commit()
            
            login_user(user, remember=True) # "remember=True" pour rester connecté à vie
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin': 
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'add_video' in request.form:
            v = Video(nom=request.form['nom'], img=request.form['img'], lien=request.form['lien'])
            db.session.add(v)
        elif 'gen_code' in request.form:
            # Génère un code unique (ex: USER-847)
            nouveau_code = f"USER-{os.urandom(2).hex().upper()}"
            u = User(code=nouveau_code, role='user')
            db.session.add(u)
        db.session.commit()
        return redirect(url_for('admin'))
    
    films = Video.query.all()
    users = User.query.filter_by(role='user').all()
    return render_template('admin.html', films=films, users=users)

@app.route('/supprimer_video/<int:id>')
@login_required
def supprimer_video(id):
    if current_user.role == 'admin':
        v = Video.query.get(id)
        db.session.delete(v)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/supprimer_user/<int:id>')
@login_required
def supprimer_user(id):
    if current_user.role == 'admin':
        u = User.query.get(id)
        db.session.delete(u)
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
