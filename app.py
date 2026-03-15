import os, uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_hdJIb9yEqX0W@ep-plain-haze-agfexo8l-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
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
def load_user(uid): return User.query.get(int(uid))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        db.session.add(User(nom="Admin", code='ADMIN123', role='admin'))
        db.session.commit()

@app.route('/')
@login_required
def index():
    return render_template('index.html', films=Video.query.all())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(code=request.form.get('code').strip()).first()
        if user:
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin': return redirect('/')
    if request.method == 'POST':
        if 'btn_add_content' in request.form:
            v = Video(nom=request.form.get('nom'), img=request.form.get('img'), lien=request.form.get('lien_film'), type=request.form.get('type'), genre=request.form.get('genre'))
            db.session.add(v); db.session.commit()
        elif 'btn_gen_code' in request.form:
            db.session.add(User(code=str(uuid.uuid4())[:8].upper())); db.session.commit()
        elif 'btn_add_episode' in request.form:
            ep = Episode(video_id=request.form.get('video_id'), saison=request.form.get('saison'), titre_ep=request.form.get('titre_ep'), lien_ep=request.form.get('lien_ep'))
            db.session.add(ep); db.session.commit()
        return redirect('/admin')
    return render_template('admin.html', films=Video.query.all(), users=User.query.filter_by(role='user').all())

@app.route('/del_v/<int:id>')
def del_v(id):
    v = Video.query.get(id)
    if v: db.session.delete(v); db.session.commit()
    return redirect('/admin')

@app.route('/del_u/<int:id>')
def del_u(id):
    u = User.query.get(id)
    if u: db.session.delete(u); db.session.commit()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
