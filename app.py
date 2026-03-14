import os, uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'la-cle-secrete-du-streamdeck'
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
    role = db.Column(db.String(20), default='user')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    img = db.Column(db.String(500))
    lien = db.Column(db.String(500))
    type = db.Column(db.String(20)) # 'film' ou 'serie'
    genre = db.Column(db.String(50), default='Autre') # NOUVEAU
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

# Initialisation forcée
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
    g = request.args.get('genre')
    query = Video.query
    if q:
        query = query.filter(Video.nom.contains(q))
    if g:
        query = query.filter(Video.genre == g)
    films = query.all()
    return render_template('index.html', films=films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code_saisi = request.form.get('code').strip()
        user = User.query.filter_by(code=code_saisi).first()
        if user:
            if user.role == 'user' and not user.nom:
                user.nom = request.form.get('nom')
                user.prenom = request.form.get('prenom')
                db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/serie/<int:id>')
@login_required
def serie_details(id):
    serie = Video.query.get_or_404(id)
    return render_template('serie.html', serie=serie)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin': return redirect(url_for('index'))
    if request.method == 'POST':
        if 'add_video' in request.form:
            v = Video(
                nom=request.form['nom'], 
                img=request.form['img'], 
                lien=request.form['lien'], 
                type=request.form['type'],
                genre=request.form['genre']
            )
            db.session.add(v)
        elif 'add_episode' in request.form:
            ep = Episode(video_id=request.form['video_id'], saison=request.form['saison'], titre_ep=request.form['titre'], lien_ep=request.form['lien_ep'])
            db.session.add(ep)
        elif 'gen_code' in request.form:
            db.session.add(User(code=str(uuid.uuid4())[:8].upper()))
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('admin.html', films=Video.query.all(), users=User.query.filter_by(role='user').all())

@app.route('/del_v/<int:id>')
@login_required
def del_v(id):
    if current_user.role == 'admin':
        db.session.delete(Video.query.get(id)); db.session.commit()
    return redirect(url_for('admin'))

@app.route('/del_u/<int:id>')
@login_required
def del_u(id):
    if current_user.role == 'admin':
        db.session.delete(User.query.get(id)); db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)import os, uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'netflix-clone-super-secret'
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
    role = db.Column(db.String(20), default='user')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    img = db.Column(db.String(500))
    lien = db.Column(db.String(500)) # Pour les films
    type = db.Column(db.String(20)) # 'film' ou 'serie'
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
    if q:
        films = Video.query.filter(Video.nom.contains(q)).all()
    else:
        films = Video.query.all()
    return render_template('index.html', films=films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code_saisi = request.form.get('code').strip()
        user = User.query.filter_by(code=code_saisi).first()
        if user:
            if user.role == 'user' and not user.nom:
                user.nom = request.form.get('nom')
                user.prenom = request.form.get('prenom')
                db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/serie/<int:id>')
@login_required
def serie_details(id):
    serie = Video.query.get_or_404(id)
    return render_template('serie.html', serie=serie)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin': return redirect(url_for('index'))
    if request.method == 'POST':
        if 'add_video' in request.form:
            v = Video(nom=request.form['nom'], img=request.form['img'], lien=request.form['lien'], type=request.form['type'])
            db.session.add(v)
        elif 'add_episode' in request.form:
            ep = Episode(video_id=request.form['video_id'], saison=request.form['saison'], titre_ep=request.form['titre'], lien_ep=request.form['lien_ep'])
            db.session.add(ep)
        elif 'gen_code' in request.form:
            db.session.add(User(code=str(uuid.uuid4())[:8].upper()))
        db.session.commit()
        return redirect(url_for('admin'))
    
    films = Video.query.all()
    users = User.query.filter_by(role='user').all()
    return render_template('admin.html', films=films, users=users)

@app.route('/del_v/<int:id>')
@login_required
def del_v(id):
    if current_user.role == 'admin':
        db.session.delete(Video.query.get(id)); db.session.commit()
    return redirect(url_for('admin'))

@app.route('/del_u/<int:id>')
@login_required
def del_u(id):
    if current_user.role == 'admin':
        db.session.delete(User.query.get(id)); db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)import os, uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ma-cle-secrete-ultra-safe'
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
    role = db.Column(db.String(20), default='user')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    img = db.Column(db.String(500))
    lien = db.Column(db.String(500))
    type = db.Column(db.String(20)) # 'film' ou 'serie'
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
    if q:
        films = Video.query.filter(Video.nom.contains(q)).all()
    else:
        films = Video.query.all()
    return render_template('index.html', films=films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code_saisi = request.form.get('code').strip()
        user = User.query.filter_by(code=code_saisi).first()
        
        if user:
            # Si c'est un invité, on enregistre son nom/prénom au 1er passage
            if user.role == 'user':
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
        if 'add_video' in request.form:
            v = Video(nom=request.form['nom'], img=request.form['img'], lien=request.form['lien'], type=request.form['type'])
            db.session.add(v)
        elif 'add_episode' in request.form:
            ep = Episode(video_id=request.form['video_id'], saison=request.form['saison'], titre_ep=request.form['titre'], lien_ep=request.form['lien_ep'])
            db.session.add(ep)
        elif 'gen_code' in request.form:
            db.session.add(User(code=str(uuid.uuid4())[:8].upper()))
        db.session.commit()
        return redirect(url_for('admin'))
    
    films = Video.query.all()
    users = User.query.filter_by(role='user').all()
    return render_template('admin.html', films=films, users=users)

@app.route('/serie/<int:id>')
@login_required
def serie_details(id):
    serie = Video.query.get_or_404(id)
    return render_template('serie.html', serie=serie)

@app.route('/del_v/<int:id>')
@login_required
def del_v(id):
    if current_user.role == 'admin':
        db.session.delete(Video.query.get(id))
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/del_u/<int:id>')
@login_required
def del_u(id):
    if current_user.role == 'admin':
        db.session.delete(User.query.get(id))
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

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
    role = db.Column(db.String(20), default='user')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    img = db.Column(db.String(500))
    lien = db.Column(db.String(500)) # Utilisé si c'est un film
    type = db.Column(db.String(20)) # 'film' ou 'serie'
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
    q = request.args.get('q') # Pour la barre de recherche
    if q:
        films = Video.query.filter(Video.nom.contains(q)).all()
    else:
        films = Video.query.all()
    return render_template('index.html', films=films)

@app.route('/serie/<int:id>')
@login_required
def serie_details(id):
    serie = Video.query.get_or_404(id)
    return render_template('serie.html', serie=serie)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(code=request.form.get('code')).first()
        if user:
            if not user.nom:
                user.nom, user.prenom = request.form.get('nom'), request.form.get('prenom')
                db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin': return redirect(url_for('index'))
    if request.method == 'POST':
        if 'add_video' in request.form:
            v = Video(nom=request.form['nom'], img=request.form['img'], lien=request.form['lien'], type=request.form['type'])
            db.session.add(v)
        elif 'add_episode' in request.form:
            ep = Episode(video_id=request.form['video_id'], saison=request.form['saison'], titre_ep=request.form['titre'], lien_ep=request.form['lien_ep'])
            db.session.add(ep)
        elif 'gen_code' in request.form:
            import uuid
            db.session.add(User(code=str(uuid.uuid4())[:8].upper()))
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('admin.html', films=Video.query.all(), users=User.query.filter_by(role='user').all())

@app.route('/del_v/<int:id>')
def del_v(id):
    db.session.delete(Video.query.get(id)); db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
