from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import pandas as pd
import random
import os

app = Flask(__name__)

# --- EXTERNAL LINKS (No local folder files needed) ---
SHEET_LINK = "https://docs.google.com/spreadsheets/d/1fiMj_RDDx9rY1KZeVfsh2Nb4hSMI933n12eGgtwU2eI/export?format=csv&gid=0"
AUDIO_URL = "https://www.dropbox.com/scl/fi/2e48j4zfdxqf9dw6hw2pe/human-heartbeat-daniel_simon.mp3?rlkey=y6d6h2a13zcnwrv8irczg3po5&raw=1"

# 1. Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'funfacts765@gmail.com' 
app.config['MAIL_PASSWORD'] = 'mohu xeye wxlk tbps' 
mail = Mail(app)
db = SQLAlchemy(app)

# 2. Database Models
class Center(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    donors = db.relationship('Donor', backref='center_link', lazy=True)

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    blood_group = db.Column(db.String(20))
    email = db.Column(db.String(100))
    center_id = db.Column(db.Integer, db.ForeignKey('center.id'))

# 3. PREMIUM UI STYLES (Animations & Sound Engine)
UI_STYLES = f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
<style>
    :root {{ --accent-red: #ff3131; --glass-panel: rgba(255, 255, 255, 0.03); --glass-border: rgba(255, 255, 255, 0.1); }}
    body {{ background: radial-gradient(circle at center, #1a1a1a 0%, #000 100%); color: #fff; font-family: 'Inter', sans-serif; margin: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh; overflow-x: hidden; }}
    .container {{ background: var(--glass-panel); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 32px; padding: 60px 40px; width: 90%; max-width: 950px; text-align: center; box-shadow: 0 40px 100px rgba(0,0,0,0.8); animation: fadeInDown 0.8s; position: relative; }}
    .heart {{ font-size: 60px; filter: drop-shadow(0 0 15px var(--accent-red)); animation: heartbeat 1.2s infinite; display: inline-block; margin-bottom: 20px; }}
    @keyframes heartbeat {{ 0% {{ transform: scale(1); }} 15% {{ transform: scale(1.25); }} 30% {{ transform: scale(1); }} }}
    .title {{ font-size: 3.2rem; font-weight: 900; background: linear-gradient(#fff, #777); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-transform: uppercase; }}
    .accent {{ color: var(--accent-red); -webkit-text-fill-color: var(--accent-red); }}
    .nav-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; margin-top: 45px; }}
    .nav-card {{ background: rgba(255, 255, 255, 0.05); border: 1px solid var(--glass-border); padding: 35px 20px; border-radius: 20px; color: #fff; text-decoration: none; font-weight: 600; transition: 0.4s; cursor: pointer; }}
    .nav-card:hover {{ transform: translateY(-12px); border-color: var(--accent-red); box-shadow: 0 20px 40px rgba(255,49,49,0.15); }}
    .signature {{ position: fixed; bottom: 20px; left: 20px; font-size: 0.8rem; color: #555; letter-spacing: 2px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
    th {{ color: #888; border-bottom: 1px solid var(--glass-border); padding: 15px; }}
    td {{ padding: 18px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
    input, select {{ background: rgba(0,0,0,0.3); color: #fff; border: 1px solid var(--glass-border); padding: 12px; border-radius: 12px; margin: 10px 0; width: 80%; }}
</style>
<audio id="heartbeat-audio" loop preload="auto"><source src="{AUDIO_URL}" type="audio/mpeg"></audio>
<script>
    window.onload = function() {{
        const audio = document.getElementById('heartbeat-audio');
        document.body.addEventListener('click', function() {{ if (audio.paused) {{ audio.play(); }} }}, {{ once: false }});
    }};
</script>
<div class="signature">MADE BY JIDON</div>
"""

@app.route('/')
def home():
    d_count = Donor.query.count()
    c_count = Center.query.count()
    return render_template_string(UI_STYLES + """
    <div class="container">
        <div class="heart">❤️</div>
        <h1 class="title">BLOOD DONATION <span class="accent">PORTAL</span></h1>
        <p style="color: #666; letter-spacing: 4px; font-size: 0.9rem; margin-top: 10px;">DONORS: {{ d_count }} | CENTERS: {{ c_count }}</p>
        <div class="nav-grid">
            <a href="/register" class="nav-card">💉 REGISTER</a>
            <a href="/search" class="nav-card" style="border-bottom: 3px solid var(--accent-red);">🔍 SEARCH</a>
            <a href="/centers" class="nav-card">🏥 CENTERS</a>
        </div>
    </div>
    """, d_count=d_count, c_count=c_count)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        bg = request.form.get('blood_group').strip().upper()
        email = request.form.get('email')
        centers = Center.query.all()
        if centers:
            new_donor = Donor(name=name, blood_group=bg, email=email, center_id=random.choice(centers).id)
            db.session.add(new_donor)
            db.session.commit()
            return render_template_string(UI_STYLES + f"""
            <div class="container animate__animated animate__jackInTheBox">
                <div style="font-size: 100px;">😊</div>
                <h1 class="accent">WELCOME ABOARD</h1>
                <p>Donor <strong>{name}</strong> added successfully!</p>
                <a href="/" class="nav-card" style="display:inline-block; margin-top:30px;">RETURN HOME</a>
            </div>
            """)
    return render_template_string(UI_STYLES + """
    <div class="container animate__animated animate__fadeInUp">
        <h1 class="accent">REGISTRATION</h1>
        <form method="POST">
            <input type="text" name="name" placeholder="Full Name" required>
            <input type="text" name="blood_group" placeholder="Blood Group (A+, A2B1+, etc.)" required>
            <input type="email" name="email" placeholder="Email Address" required>
            <button type="submit" class="nav-card" style="cursor:pointer; background:none; width:50%; margin-top:20px;">BECOME A DONOR</button>
        </form>
        <br><a href="/" style="color: #555; text-decoration: none;">Back</a>
    </div>
    """)

@app.route('/centers')
def centers():
    c_list = Center.query.all()
    return render_template_string(UI_STYLES + """
    <div class="container animate__animated animate__fadeInRight">
        <h1 class="accent">HOSPITAL NETWORK</h1>
        <div class="nav-grid">
            {% for h in c_list %}
            <div class="nav-card"><h3>{{ h.name }}</h3><p style="color: #888;">📍 {{ h.location }}</p></div>
            {% endfor %}
        </div>
        <br><a href="/" style="color: #555; text-decoration: none;">Back</a>
    </div>
    """, c_list=c_list)

@app.route('/apply/<int:d_id>', methods=['POST'])
def apply_blood(d_id):
    donor = Donor.query.get_or_404(d_id)
    hospital = Center.query.get(request.form.get('h_id'))
    msg = Message('URGENT: Blood Request', sender=app.config['MAIL_USERNAME'], recipients=[donor.email])
    msg.body = f"Hello {donor.name}, urgent {donor.blood_group} blood requested at {hospital.name}."
    try:
        mail.send(msg)
        return render_template_string(UI_STYLES + f"""
        <div class="container animate__animated animate__zoomIn">
            <div style="font-size: 100px; color: #4CAF50;">✔️</div>
            <h1 style="color: #4CAF50;">SUCCESS</h1>
            <p>Email sent to <strong>{donor.name}</strong> Successfully!</p>
            <a href="/" class="nav-card" style="display:inline-block; margin-top:30px;">RETURN HOME</a>
        </div>
        """)
    except Exception as e:
        return f"Error: {e}"

@app.route('/search')
def search():
    query_bg = request.args.get('blood_group', '').strip().upper()
    results = Donor.query.filter(Donor.blood_group == query_bg).all() if query_bg else []
    hospitals = Center.query.all()
    return render_template_string(UI_STYLES + """
    <div class="container animate__animated animate__fadeIn">
        <h1 class="accent">FIND BLOOD</h1>
        <form action="/search">
            <input type="text" name="blood_group" placeholder="Enter Exact Group (e.g., A2B1+)" style="width: 350px;">
            <button type="submit" class="nav-card" style="padding: 12px 25px; cursor:pointer; background:none;">SEARCH</button>
        </form>
        {% if donors %}
        <table>
            <tr><th>Name</th><th>Group</th><th>Select Hospital</th><th>Action</th></tr>
            {% for d in donors %}
            <tr>
                <td>{{ d.name }}</td><td style="color:var(--accent-red); font-weight:bold;">{{ d.blood_group }}</td>
                <form action="/apply/{{ d.id }}" method="POST">
                <td><select name="h_id">{% for h in hospitals %}<option value="{{ h.id }}">{{ h.name }}</option>{% endfor %}</select></td>
                <td><button type="submit" class="nav-card" style="padding: 8px 20px; border-color: var(--accent-red); color: var(--accent-red); background:none;">EMAIL</button></td>
                </form>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
        <br><a href="/" style="color: #555; text-decoration: none;">Back</a>
    </div>
    """, donors=results, hospitals=hospitals)

def seed_data():
    with app.app_context():
        db.create_all()
        if Center.query.first() is None:
            tn_centers = [("Rajiv Gandhi Govt Hospital", "Chennai"), ("Government Stanley Hospital", "Chennai"), ("Thanjavur Govt Medical College", "Thanjavur"), ("Cuddalore Govt Hospital", "Cuddalore"), ("Salem Govt Hospital", "Salem"), ("Trichy Govt Hospital", "Trichy"), ("Coimbatore Govt Hospital", "Coimbatore")]
            c_list = [Center(name=n, location=l) for n, l in tn_centers]
            db.session.add_all(c_list)
            db.session.commit()
            try:
                df = pd.read_csv(SHEET_LINK)
                for _, row in df.iterrows():
                    name = str(row.get('donar name', '')).strip()
                    if name and name != 'nan':
                        db.session.add(Donor(name=name, blood_group=str(row.get('Blood Group', '')).strip().upper(), email=str(row.get('Email', '')).strip(), center_id=random.choice(c_list).id))
                db.session.commit()
            except: pass

seed_data()
if __name__ == '__main__':
    app.run(debug=True)