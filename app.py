import os, uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle-secrete-streamdeck-2026'

# --- CONNEXION NEON ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_hdJIb9yEqX0W@ep-plain-haze-agfexo8l-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODÈLES ---
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
    lien = db.Column(db.String(500)) # Pour les films
    type = db.Column(db.String(20)) # 'film' ou 'serie'
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
    if q: query = query.filter(Video.nom.ilike(f'%{q}%'))
    if genre_f: query = query.filter(Video.genre == genre_f)
    return render_template('index.html', films=query.all())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code_s = request.form.get('code').strip()
        user = User.query.filter_by(code=code_s).first()
        if user:
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin': return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Ajouter Film ou Série
        if 'add_content' in request.form:
            v_type = request.form['type']
            new_v = Video(
                nom=request.form['nom'], 
                img=request.form['img'], 
                lien=request.form.get('lien_film'), 
                type=v_type, 
                genre=request.form['genre']
            )
            db.session.add(new_v)
            db.session.flush() # Pour récupérer l'ID
            
            # Si c'est une série, on ajoute le premier épisode
            if v_type == 'serie' and request.form.get('saison'):
                ep = Episode(
                    video_id=new_v.id, 
                    saison=request.form['saison'], 
                    titre_ep=request.form['titre_ep'], 
                    lien_ep=request.form['lien_ep']
                )
                db.session.add(ep)
        
        # Ajouter un épisode à une série existante
        elif 'add_episode' in request.form:
            ep = Episode(
                video_id=request.form['video_id'],
                saison=request.form['saison'],
                titre_ep=request.form['titre_ep'],
                lien_ep=request.form['lien_ep']
            )
            db.session.add(ep)

        # Générer un code
        elif 'gen_code' in request.form:
            db.session.add(User(code=str(uuid.uuid4())[:8].upper()))
        
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('admin.html', films=Video.query.all(), users=User.query.filter_by(role='user').all())

@app.route('/serie/<int:id>')
@login_required
def serie_details(id):
    s = Video.query.get_or_404(id)
