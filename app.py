import os, uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'streamdeck-ultra-secure-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODÈLES DE DONNÉES ---
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

# Initialisation de la base de données
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
    if current_user.role != 'admin': 
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Action : Ajouter un film ou une série
        if 'add_content' in request.form:
            v_type = request.form.get('type')
            v = Video(
                nom=request.form.get('nom'),
                img=request.form.get('img'),
                lien=request.form.get('lien_film') if v_type == 'film' else None,
                type=v_type,
                genre=request.form.get('genre')
            )
            db.session.add(v)
            db.session.flush()
            
            if v_type == 'serie':
                ep = Episode(
                    video_id=v.id,
                    saison=f"Saison {request.form.get('saison')}",
                    titre_ep=f"Épisode {request.form.get('titre_ep')}",
                    lien_ep=request.form.get('lien_ep')
                )
                db.session.add(ep)
        
        # Action : Générer un code unique
        elif 'gen_code' in request.form:
            nouveau_code = str(uuid.uuid4())[:8].upper()
            db.session.add(User(code=nouveau_code, role='user'))
            
        db.session.commit()
        return redirect(url_for('admin'))

    # Récupération des données pour l'affichage
    tous_les_films = Video.query.all()
    tous_les_utilisateurs = User.query.filter_by(role='user').all()
    return render_template('admin.html', films=tous_les_films, users=tous_les_utilisateurs)

@app.route('/del_v/<int:id>')
@login_required
def del_v(id):
    if current_user.role == 'admin':
        video = Video.query.get(id)
        if video:
            db.session.delete(video)
            db.session.commit()
    return redirect(url_for('admin'))

@app.route('/del_u/<int:id>')
@login_required
def del_u(id):
    if current_user.role == 'admin':
        user = User.query.get(id)
        if user:
            db.session.delete(user)
            db.session.commit()
    return redirect(url_for('admin'))

@app.route('/serie/<int:id>')
@login_required
def serie_details(id):
    serie = Video.query.get_or_404(id)
    return render_template('serie.html', serie=serie)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
