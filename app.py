import os, uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle-secrete-streamdeck-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODÈLES (Base de données) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    code = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(20), default='user')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    img = db.Column(db.String(500))
    lien = db.Column(db.String(500)) 
    type = db.Column(db.String(20)) 
    genre = db.Column(db.String(50))
    episodes = db.relationship('Episode', backref='video', cascade="all, delete-orphan")

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    saison = db.Column(db.String(50))
    titre_ep = db.Column(db.String(200))
    lien_ep = db.Column(db.String(500))

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

with app.app_context():
    db.create_all()
    # Création du compte admin par défaut si inexistant
    if not User.query.filter_by(role='admin').first():
        db.session.add(User(nom="Admin", prenom="Boss", code='ADMIN123', role='admin'))
        db.session.commit()

# --- ROUTES ---

@app.route('/')
@login_required
def index():
    q = request.args.get('q')
    genre_f = request.args.get('genre')
    query = Video.query
    if q: query = query.filter(Video.nom.contains(q))
    if genre_f: query = query.filter(Video.genre == genre_f)
    return render_template('index.html', films=query.all())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code_s = request.form.get('code', '').strip()
        user = User.query.filter_by(code=code_s).first()
        if user:
            if user.role == 'user' and not user.nom:
                user.nom = request.form.get('nom')
                user.prenom = request.form.get('prenom')
                db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin': return redirect(url_for('index'))
    if request.method == 'POST':
        # Action : Créer un nouveau contenu (Film ou Série)
       if __name__ == '__main__':
    # Render définit automatiquement un PORT, on doit l'utiliser
    port = int(os.environ.get("PORT", 5000))
    # On force l'écoute sur 0.0.0.0 pour que Render puisse voir l'app
    app.run(host='0.0.0.0', port=port)
