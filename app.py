from flask import Flask, render_template, request, redirect, url_for, session,jsonify
import sqlite3
from model import predict_e_waste
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'binarybrain@Greenbits2025'

# UPLOAD_FOLDER = "images"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

# Set the upload folder in app configuration
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

E_WASTE_HANDLING_STEPS = {
     "Television": [
        "Donate working TVs to schools or charities.",
        "Take broken TVs to an authorized e-waste recycling center.",
        "Avoid dumping CRT TVs as they contain hazardous lead.",
        "Consider repurposing parts like screens for DIY projects."
    ],
    "Keyboard": [
        "Clean and repair instead of replacing.",
        "Donate old keyboards to NGOs or schools.",
        "Send broken keyboards to e-waste recyclers.",
        "Use keycaps for creative projects or spare parts."
    ],
    "Mouse": [
        "Try fixing unresponsive buttons before discarding.",
        "Use old mice for DIY projects like robotics.",
        "Drop off at a certified e-waste collection center."
    ],
    "PCB": [
        "Extract useful components before disposal.",
        "Recycle PCBs at specialized e-waste centers.",
        "Never burn PCBs as they release toxic chemicals."
    ],
    "Mobile": [
        "Donate or sell – If your phone is in working condition, donate it to charities or sell it on platforms like eBay, OLX, or Swappa.",
        "Trade-in programs – Many brands like Apple, Samsung, and OnePlus offer exchange programs for old devices.",
        "Proper recycling – If the phone is completely non-functional, take it to authorized e-waste recycling centers.",
        "Remove personal data – Before disposing of your phone, erase all data and perform a factory reset."
    ],
    "Washing Machine": [
        "Repair before disposal – If the washing machine has minor issues, consider repairing it instead of discarding it.",
        "Exchange offers – Many appliance brands offer discounts when you trade in an old washing machine for a new one.",
        "Donate to charity – If the machine is in working condition, donate it to local NGOs, orphanages, or shelters.",
        "Recycle responsibly – Contact authorized e-waste recyclers who can dismantle and process materials safely."
    ],
    "Microwave": [
        "Repair instead of replace – If your microwave has minor issues like a broken button or fuse, get it repaired instead of discarding it.",
        "Donate if functional – If it still works, donate it to charities, community centers, or someone in need.",
        "Reuse parts – Components like the turntable, glass plate, and motor can be repurposed for DIY projects or repairs.",
        "Recycle properly – Non-functional microwaves contain metal and electronic parts that should be recycled at certified e-waste collection centers."
    ],
    "Printer": [
        "Repair for small issues – Fix minor problems like paper jams or roller replacements instead of discarding the printer.",
        "Refill ink instead of replacing – Instead of buying a new printer, refill ink cartridges to extend its lifespan.",
        "Recycle cartridges properly – Many manufacturers and stores offer recycling programs for used ink and toner cartridges.",
        "Disassemble for recycling – Printers contain plastic, metal, and electronic boards—send them to certified recyclers to avoid landfill waste."
    ],
    "Can't Determine": [
        "Ensure the image is clear and contains a single item.",
        "Try retaking the picture with better lighting.",
        "Consult a local e-waste expert for proper disposal."
    ]
}


# def get_db_connection():
#     conn = sqlite3.connect("users.db")
#     conn.row_factory = sqlite3.Row
#     return conn

def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False, timeout=10)  # Added timeout
    conn.row_factory = sqlite3.Row
    return conn


def get_db_connection2():
    conn=sqlite3.connect("organisation.db")
    conn.row_factory=sqlite3.Row
    return conn 




@app.route('/')
def landing():
    return render_template('index2.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)  # Hash password

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return render_template('signup.html', error="Username already exists")

    return render_template('signup.html')


@app.route('/orgsign', methods=['GET', 'POST'])
def orgsign():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmpassword=request.form['confirm password']

        # hashed_password = generate_password_hash(password)

        if password!=confirmpassword:
            return render_template('orgsign.html',error="password doesn't matched")

        hashed_password = generate_password_hash(password)  # Hash password

        conn = get_db_connection2()
        try:
            conn.execute("INSERT INTO organisation (orgname, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('orglogin'))
        except:
            return render_template('orgsign.html', error="Username already exists")

    return render_template('orgsign.html')


@app.route('/orglogin', methods=['GET', 'POST'])
def orglogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection2()
        user = conn.execute("SELECT * FROM organisation WHERE orgname = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            
            # Store login event
            conn = get_db_connection2()
            conn.execute("INSERT INTO login_activity_organisation (orgname) VALUES (?)", (username,))
            conn.commit()
            conn.close()
            
            return redirect(url_for('home'))
        else:
            return render_template('orglogin.html', error="Invalid Credentials")

    return render_template('orglogin.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         conn = get_db_connection()
#         user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
#         conn.close()

#         if user and check_password_hash(user['password'], password):
#             # Ensure user has a profile photo; fallback to default if missing
#             # profile_photo = user['profile_photo'] if user['profile_photo'] else "/static/images/default.png"

#             # Store user session
#             session['user'] = {
#                 "username": user['username'],
#                 # "profile_photo": profile_photo
#             }

#             # Store login event
#             conn = get_db_connection()
#             conn.execute("INSERT INTO login_activity (username) VALUES (?)", (username,))
#             conn.commit()
#             conn.close()

#             return render_template('personhome.html', sendname=user['username'])
#         else:
#             return render_template('login.html', error="Invalid Credentials")

#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            
            # Store login event
            conn = get_db_connection()
            conn.execute("INSERT INTO login_activity (username) VALUES (?)", (username,))
            conn.commit()
            conn.close()
            
            # return redirect(url_for('personhome'))
            return render_template('personhome.html', sendname=username)
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')



@app.route('/admin')
def admin():
    if "user" not in session or session["user"] != "admin":
        return "Access Denied"

    conn = get_db_connection()
    logins = conn.execute("SELECT * FROM login_activity ORDER BY login_time DESC").fetchall()
    conn.close()

    conn2 = get_db_connection2()
    logins2 = conn2.execute("SELECT * FROM login_activity_organisation ORDER BY login_time DESC").fetchall()
    conn2.close()
    
    return render_template('admin.html', logins=logins, logins2=logins2)

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Make prediction
        predicted_label, confidence = predict_e_waste(filepath)
        confidence = float(confidence)
        if confidence < 0.8:
            predicted_label = "Can't Determine"

        handling_steps = E_WASTE_HANDLING_STEPS.get(predicted_label, ["No handling steps available."])        

        return jsonify({"prediction": predicted_label, "confidence": f"{confidence:.2f}","handling_steps": handling_steps})


if __name__ == '__main__':
    app.run(debug=True)
