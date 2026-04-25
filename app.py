import os
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from flask import (Flask, render_template, redirect, url_for,
                   request, flash, abort)
from flask_login import (LoginManager, login_user, login_required,
                         logout_user, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models import db, User, Fabric, Selection, Design

load_dotenv()

# ─────────────────────────────────────────────
#  App configuration
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "tohfa_dev_secret_2026")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root@localhost/tohfa_db")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root@localhost/nom_de_ta_base_locale')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024   # 16 MB max upload

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'designs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)
csrf = CSRFProtect(app)

# ─────────────────────────────────────────────
#  Railway Initialization (CRITIQUE POUR GUNICORN)
# ─────────────────────────────────────────────
with app.app_context():
    try:
        db.create_all()
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        print("✅ Base de données et dossiers initialisés.")
    except Exception as e:
        print(f"❌ Erreur d'initialisation : {e}")

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Veuillez vous connecter pour continuer."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─────────────────────────────────────────────
#  Role-based decorators
# ─────────────────────────────────────────────
def client_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_client:
            flash("Espace réservé aux clients.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def designer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_designer:
            flash("Espace réservé aux designers.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

# ─────────────────────────────────────────────
#  Authentication routes
# ─────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('designer_dashboard') if current_user.is_designer
                        else url_for('fabrics'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            flash(f"Bienvenue, {user.full_name} ✨", "success")
            return redirect(url_for('designer_dashboard') if user.is_designer
                            else url_for('fabrics'))
        flash("Email ou mot de passe incorrect.", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role', 'client')
        margin = float(request.form.get('margin_pct', 15)) / 100

        new_user = User(
            full_name=request.form['name'],
            email=request.form['email'],
            phone_number=request.form['phone'],
            password_hash=generate_password_hash(request.form['password']),
            role=role,
            margin_pct=margin if role == 'designer' else 0.0,
            bio=request.form.get('bio', ''),
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Compte créé avec succès ✨", "success")
            return redirect(url_for('login'))
        except Exception:
            db.session.rollback()
            flash("Cet email est déjà utilisé.", "danger")
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté(e).", "info")
    return redirect(url_for('login'))

# ─────────────────────────────────────────────
#  CLIENT routes
# ─────────────────────────────────────────────
@app.route('/fabrics')
@login_required
@client_required
def fabrics():
    all_fabrics = Fabric.query.filter_by(availability=True).all()
    return render_template('client/fabrics.html', fabrics=all_fabrics)

@app.route('/select/fabric/<int:fabric_id>')
@login_required
@client_required
def select_fabric(fabric_id):
    sel = Selection.query.filter_by(client_id=current_user.user_id).first()
    if sel:
        sel.fabric_id = fabric_id
        sel.updated_at = datetime.utcnow()
    else:
        sel = Selection(client_id=current_user.user_id, fabric_id=fabric_id)
        db.session.add(sel)
    db.session.commit()
    flash("Tissu sélectionné ✔", "success")
    return redirect(url_for('fabrics'))

@app.route('/designs')
@login_required
@client_required
def designs():
    all_designs = Design.query.filter_by(is_active=True).all()
    return render_template('client/designs.html', designs=all_designs)

@app.route('/select/design/<int:design_id>')
@login_required
@client_required
def select_design(design_id):
    sel = Selection.query.filter_by(client_id=current_user.user_id).first()
    if sel:
        sel.design_id = design_id
        sel.updated_at = datetime.utcnow()
    else:
        sel = Selection(client_id=current_user.user_id, design_id=design_id)
        db.session.add(sel)
    db.session.commit()
    flash("Design sélectionné ✔", "success")
    return redirect(url_for('designs'))

@app.route('/my-selection')
@login_required
@client_required
def my_selection():
    sel = Selection.query.filter_by(client_id=current_user.user_id).first()
    return render_template('client/my_selection.html', selection=sel)

# ── TF-IDF recommendation ──────────────────────────────────────
def compute_tfidf_similarities(reference_fabric, all_fabrics):
    if not reference_fabric or not reference_fabric.description:
        return {}
    corpus, fabric_ids = [], []
    for f in all_fabrics:
        if f.description:
            corpus.append(f.description)
            fabric_ids.append(f.fabric_id)
    if not corpus:
        return {}
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(corpus)
    ref_vector = vectorizer.transform([reference_fabric.description])
    similarities = cosine_similarity(ref_vector, tfidf_matrix).flatten()
    return dict(zip(fabric_ids, similarities))

@app.route('/recommend')
@login_required
@client_required
def recommend():
    user_choice = Selection.query.filter_by(client_id=current_user.user_id).first()
    popular_counts = db.session.query(
        Selection.fabric_id, func.count(Selection.fabric_id).label('total')
    ).group_by(Selection.fabric_id).all()
    popular_ids = [item.fabric_id for item in popular_counts]

    fav_color, chosen_fabric = "", None
    if user_choice:
        chosen_fabric = Fabric.query.get(user_choice.fabric_id)
        colors = ["Azur", "Bleu", "Or", "Doré", "Rosé", "Gris",
                  "Noir", "Vert", "Rouge", "Argent"]
        if chosen_fabric:
            for c in colors:
                if c.lower() in chosen_fabric.name.lower():
                    fav_color = c.lower()
                    break

    all_fabrics = Fabric.query.filter_by(availability=True).all()
    tfidf_scores = {}
    if chosen_fabric:
        tfidf_scores = compute_tfidf_similarities(chosen_fabric, all_fabrics)

    recommendations = []
    for fabric in all_fabrics:
        if user_choice and fabric.fabric_id == user_choice.fabric_id:
            continue
        score = (0.6 * tfidf_scores.get(fabric.fabric_id, 0)
                 + (0.25 if fabric.fabric_id in popular_ids else 0)
                 + (0.15 if fav_color and fav_color in fabric.name.lower() else 0))
        recommendations.append((fabric, round(score, 3)))

    recommendations.sort(key=lambda x: x[1], reverse=True)
    return render_template('client/recommend.html', fabrics=recommendations[:6])

# ─────────────────────────────────────────────
#  DESIGNER routes
# ─────────────────────────────────────────────
@app.route('/designer/dashboard')
@login_required
@designer_required
def designer_dashboard():
    my_designs = Design.query.filter_by(designer_id=current_user.user_id).all()
    earnings = current_user.total_earnings()
    selections_count = current_user.total_selections()
    return render_template('designer/dashboard.html',
                           designs=my_designs,
                           earnings=earnings,
                           selections_count=selections_count)

@app.route('/designer/upload', methods=['GET', 'POST'])
@login_required
@designer_required
def designer_upload():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = float(request.form.get('price', 500))
        file = request.files.get('image')

        if not name:
            flash("Le nom du design est requis.", "danger")
            return redirect(url_for('designer_upload'))

        image_url = None
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.user_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"/static/uploads/designs/{filename}"

        new_design = Design(
            designer_id=current_user.user_id,
            name=name,
            description=description,
            price=price,
            image_url=image_url,
        )
        db.session.add(new_design)
        db.session.commit()
        flash(f"Design « {name} » publié avec succès ✨", "success")
        return redirect(url_for('designer_dashboard'))

    return render_template('designer/upload.html')

@app.route('/designer/design/<int:design_id>/toggle', methods=['POST'])
@login_required
@designer_required
def designer_toggle_design(design_id):
    design = Design.query.get_or_404(design_id)
    if design.designer_id != current_user.user_id:
        abort(403)
    design.is_active = not design.is_active
    db.session.commit()
    status = "activé" if design.is_active else "désactivé"
    flash(f"Design {status}.", "info")
    return redirect(url_for('designer_dashboard'))

@app.route('/designer/design/<int:design_id>/delete', methods=['POST'])
@login_required
@designer_required
def designer_delete_design(design_id):
    design = Design.query.get_or_404(design_id)
    if design.designer_id != current_user.user_id:
        abort(403)
    # Remove image file if exists
    if design.image_url:
        img_path = os.path.join(os.getcwd(), design.image_url.lstrip('/'))
        if os.path.exists(img_path):
            os.remove(img_path)
    db.session.delete(design)
    db.session.commit()
    flash("Design supprimé.", "warning")
    return redirect(url_for('designer_dashboard'))

# ─────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)