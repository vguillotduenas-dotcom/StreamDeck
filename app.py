import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle-secrete-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(20))

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    img = db.Column(db.String(500))
    lien = db.Column(db.String(500))

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

# --- CRÉATION AUTOMATIQUE DES TABLES ---
# Cette fonction s'exécute AVANT la première requête pour éviter l'erreur "no such table"
@app.before_request
def setup():
    db.create_all()
    if not User.query.filter_by(code='ADMIN123').first():
        admin = User(code='ADMIN123', role='admin')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
@login_required
def index():
    tous_les_films = Video.query.all()
    return render_template('index.html', films=tous_les_films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_code = request.form.get('code')
        # On vérifie si la table existe avant de chercher (double sécurité)
        try:
            u = User.query.filter_by(code=user_code).first()
            if u:
                login_user(u)
                return redirect(url_for('index'))
        except:
            return "Initialisation en cours... rafraîchissez la page."
    return render_template('login.html')

@app.route('/supprimer/<int:id>')
@login_required
def supprimer(id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    film = Video.query.get(id)
    if film:
        db.session.delete(film)
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
