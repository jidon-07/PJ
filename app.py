from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import pandas as pd
import random
import os

app = Flask(__name__)

SHEET_LINK = "https://docs.google.com/spreadsheets/d/1fiMj_RDDx9rY1KZeVfsh2Nb4hSMI933n12eGgtwU2eI/export?format=csv&gid=0"
AUDIO_URL = "https://www.dropbox.com/scl/fi/2e48j4zfdxqf9dw6hw2pe/human-heartbeat-daniel_simon.mp3?rlkey=y6d6h2a13zcnwrv8irczg3po5&raw=1"

# ================= CONFIG =================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ FIXED FOR RENDER
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('funfacts765@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('stdt ijlu qyqz amai')
app.config['MAIL_TIMEOUT'] = 10

mail = Mail(app)
db = SQLAlchemy(app)

# ================= MODELS =================
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

# ================= UI =================
UI_STYLES = f"""
<style>
body {{ background:black; color:white; text-align:center; font-family:Arial }}
.container {{ padding:40px }}
</style>
"""

# ================= HOME =================
@app.route('/')
def home():
    d_count = Donor.query.count()
    c_count = Center.query.count()
    return render_template_string(UI_STYLES + f"""
    <div class="container">
    <h1>Blood Donation Portal</h1>
    Donors: {d_count} | Centers: {c_count}
    <br><br>
    <a href="/register">Register</a><br>
    <a href="/search">Search</a><br>
    <a href="/centers">Centers</a>
    </div>
    """)

# ================= REGISTER =================
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form['name']
        bg=request.form['blood_group']
        email=request.form['email']
        c=random.choice(Center.query.all())
        db.session.add(Donor(name=name,blood_group=bg,email=email,center_id=c.id))
        db.session.commit()
        return redirect('/')
    return render_template_string(UI_STYLES + """
    <div class="container">
    <form method="POST">
    <input name="name"><br>
    <input name="blood_group"><br>
    <input name="email"><br>
    <button>Submit</button>
    </form>
    </div>
    """)

# ================= CENTERS =================
@app.route('/centers')
def centers():
    data=Center.query.all()
    return render_template_string(UI_STYLES + """
    <div class="container">
    {% for c in data %}
    {{ c.name }} - {{ c.location }}<br>
    {% endfor %}
    </div>
    """,data=data)

# ================= SEARCH =================
@app.route('/search')
def search():
    donors=Donor.query.all()
    centers=Center.query.all()
    return render_template_string(UI_STYLES + """
    <div class="container">
    {% for d in donors %}
    <form action="/apply/{{d.id}}" method="POST">
    {{d.name}} - {{d.blood_group}}
    <select name="h_id">
    {% for h in centers %}
    <option value="{{h.id}}">{{h.name}}</option>
    {% endfor %}
    </select>
    <button>Send</button>
    </form>
    {% endfor %}
    </div>
    """,donors=donors,centers=centers)

# ================= APPLY (FIXED) =================
@app.route('/apply/<int:d_id>', methods=['POST'])
def apply_blood(d_id):
    donor = Donor.query.get_or_404(d_id)
    hospital = Center.query.get(request.form.get('h_id'))

    try:
        msg = Message(
            'URGENT: Blood Request',
            sender=app.config['MAIL_USERNAME'],
            recipients=[donor.email]
        )
        msg.body = f"Hello {donor.name}, urgent {donor.blood_group} blood requested at {hospital.name}."

        mail.send(msg)

        return render_template_string(UI_STYLES + f"""
        <div class="container">
        <h2 style='color:green'>SUCCESS</h2>
        Email sent to {donor.name}
        <br><a href="/">Back</a>
        </div>
        """)

    except Exception as e:
        print("MAIL ERROR:", e)

        return render_template_string(UI_STYLES + f"""
        <div class="container">
        <h2 style='color:orange'>MAIL FAILED</h2>
        System working but email failed
        <br><a href="/">Back</a>
        </div>
        """)

# ================= SEED =================
def seed():
    with app.app_context():
        db.create_all()
        if Center.query.first() is None:
            centers=[
                Center(name="Chennai GH",location="Chennai"),
                Center(name="Salem GH",location="Salem")
            ]
            db.session.add_all(centers)
            db.session.commit()

            db.session.add(Donor(name="Test",blood_group="A+",email="test@gmail.com",center_id=1))
            db.session.commit()

seed()

# ================= RUN =================
if __name__ == '__main__':
    app.run()
