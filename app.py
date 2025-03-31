from flask import Flask,  render_template, request, redirect, url_for, session,jsonify
import sqlite3 
import requests
from model import predict_e_waste 
import firebase_admin
from firebase_admin import credentials, firestore
import os 
import joblib 
from google.cloud import storage
from dotenv import load_dotenv 
load_dotenv()
import pandas as pd
from werkzeug.utils import secure_filename 
from flask_cors import CORS
from datetime import datetime 
import googleapiclient.discovery 
import google.generativeai as genai 
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


CORS(app)

cred = credentials.Certificate("firebase-admin-sdk.json")  
firebase_admin.initialize_app(cred)
db = firestore.client()

GOOGLE_MAPS_API_KEY = os.getenv("MAP_KEY")



genai.configure(api_key=os.getenv("GENAI_API_KEY")) 

df = pd.read_csv("ewaste_collection_centers_full.csv") 

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 


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









@app.route('/')
def landing():
    return render_template('index2.html')

@app.route('/home')
def home():
    return render_template('home.html')


@app.route("/logout", methods=["POST"])
def logout():
    session.clear() 
    return jsonify({"message": "Logged out"}), 200





@app.route("/org_signin", methods=["POST"])
def org_signin():
    try:
        data = request.get_json()
        uid = data.get("uid")
        email = data.get("email")
        name=data.get("name")

        if not uid or not email:
            print("❌ Missing required fields:", data)
            return jsonify({"error": "Missing required fields"}), 400

        org_ref = db.collection("organizations").document(uid)
        org_doc = org_ref.get()

        

        if org_doc.exists:
            org_data = org_doc.to_dict()
            print(f"📢 User {uid} found in DB:", org_data)

            
        else:
            print("🆕 New user! Creating record...")
            org_ref.set({
                "uid": uid,
                "email": email,
                "name":name,
                "created_at": datetime.utcnow()
            })
            

        
        return jsonify({
            "message": "Sign-in successful!"
            
        }), 200

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({"error": str(e)}), 500





@app.route("/organisation")
def organisation_page():
    return render_template("organisation.html")




@app.route("/login", methods=["POST"])
def google_login():


    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400 
        
        uid = data.get("uid")
        name = data.get("name")
        email = data.get("email")
        profile_picture = data.get("profile_picture")

        if not uid or not email:
            return jsonify({"error": "Invalid data"}), 400
        
        greenbit_query = db.collection("greenBitsDatabase").where("customer_id", "==", uid).stream()
        for greenbit_doc in greenbit_query:
            greenbit_data = greenbit_doc.to_dict()

        # 2. Check if received == 0
            if greenbit_data.get("received") == 0:
                green_bits_amount = greenbit_data.get("green_bits", 0)

            # 3. Find the user in users2 database
                user_ref = db.collection("users2").document(uid)
                user_doc = user_ref.get()

                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    updated_greenbits = user_data.get("greenbits", 0) + green_bits_amount

                # 4. Update the user's greenbits in users2
                    user_ref.update({"greenbits": updated_greenbits})

                # 5. Mark received as 1 in greenbitsDatabase
                    greenbit_doc_ref = db.collection("greenBitsDatabase").document(greenbit_doc.id)
                    greenbit_doc_ref.update({"received": 1})

                    # return jsonify({"message": "Greenbits updated successfully"}), 200







        user_ref = db.collection("users2").document(uid)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            user_ref.update({"last_login": datetime.utcnow()})
        else:
            user_data = {
                "uid": uid,
                "name": name,
                "email": email,
                "profile_picture": profile_picture,
                "greenbits": 5,  
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow(),
            }
            user_ref.set(user_data)

        session["user"] = {
            "uid": uid,
            "name": name,
            "email": email,
            "profile_picture": profile_picture,
            "greenbits": user_data.get("greenbits", 5)
        }   

        
        return jsonify(user_data), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Server error", "message": str(e)}), 500
    


@app.route('/get_organizations', methods=['GET'])
def get_organizations():
    """Fetch all organizations from Firebase Firestore"""
    organizations_ref = db.collection("organizations")  
    docs = organizations_ref.stream()

    org_list = []
    for doc in docs:
        data = doc.to_dict()
        org_list.append({
            "uid": data.get("uid"),
            "name": data.get("name"),
            "email": data.get("email"),
            "image": data.get("image_url", "static/images/tree.jpg")  
        })

    return jsonify(org_list)  




@app.route("/personhome")
def person_home():

    if "user" not in session:
        return redirect(url_for("landing_page"))  

    user_data = session["user"]
    return render_template("personhome.html", user=user_data)




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

        
        predicted_label, confidence = predict_e_waste(filepath)
        confidence = float(confidence)
        if confidence < 0.8:
            predicted_label = "Can't Determine"

        handling_steps = E_WASTE_HANDLING_STEPS.get(predicted_label, ["No handling steps available."])        

        return jsonify({"prediction": predicted_label, "confidence": f"{confidence:.2f}","handling_steps": handling_steps})


@app.route("/get_organization_requests", methods=["POST"])
def get_organization_requests():
    try:
        data = request.json
        org_id = data.get("org_id")  

        if not org_id:
            return jsonify({"error": "Organization ID is required"}), 400

        products_ref = db.collection("products")
        requests = []

        
        query = products_ref.stream()
        
        for doc in query:
            product_data = doc.to_dict()
            product_data["product_id"] = doc.id
            org_list = product_data.get("organizations", [])

            
            if "all" in org_list or org_id in org_list:
                requests.append(product_data)

        return jsonify({"requests": requests}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/submit_product", methods=["POST"])
def submit_product():
    try:
        data = request.json
        doc_ref = db.collection("products").document()
        product_data = {
            "product_id": doc_ref.id,
            "product_name": data["product_name"],
            "product_age": data["product_age"],
            "brand": data["brand"],
            "model": data["model"],
            "description": data["description"],
            "user_id": data["user_id"],
            "email": data["email"],
            "organizations": data["organizations"],
            "created_at": firestore.SERVER_TIMESTAMP
        }

       
        db.collection("products").add(product_data)

        return jsonify({"message": "Product submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/get-ewaste/<org_id>", methods=["GET"])
def get_ewaste(org_id):
    products = db.collection("e_waste_products").stream()
    result = []

    for product in products:
        product_data = product.to_dict()
        if "selected_organizations" in product_data and (org_id in product_data["selected_organizations"] or "all" in product_data["selected_organizations"]):
            result.append(product_data)

    return jsonify(result)

@app.route("/store_message", methods=["POST"])
def store_message():
    try:
       
        data = request.json
        organization_name = data.get("organizationName")
        organization_id = data.get("organizationId")
        user_id = data.get("selectedUserId")
        product_id = data.get("selectedProductId")
        product_name = data.get("selectedProductName")
        model=data.get("selectedModel")
        message_type = data.get("messageType")  
        message = data.get("message")
        estimated_price = data.get("estimatedPrice")


        doc_ref = db.collection("products").document(product_id)
       
        doc_ref.set({"status": "Accepted"}, merge=True)

        
        if not all([organization_id, user_id, message_type]):
            return jsonify({"error": "Missing required fields"}), 400

       
        doc_ref = db.collection("individualMessage").document()
        doc_ref.set({
            "organizationName": organization_name,
            "organizationId": organization_id,
            "userId": user_id,
            "productId": product_id,
            "productName": product_name,
            "model":model,
            "messageType": message_type,
            "message": message,
            "estimatedPrice": estimated_price,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"success": True, "message": "Data stored successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_notifications", methods=["GET"])
def get_notifications():
    if "user" not in session:
        return jsonify({"message": "User not logged in"}), 403

    user = session["user"]
    user_id = user["uid"]  # Get stored UID

    print("Fetching notifications for user:", user_id)  # Debugging

    messages_ref = db.collection("individualMessage")
    messages_query = messages_ref.where("userId", "==", user_id).stream()

    notifications = []
    for message in messages_query:
        data = message.to_dict()
        notification_text = f"{data.get('messageType', 'Update')} - {data.get('productName', '')} {data.get('model', '')} <br> product_id- {data.get('productId', '')} by {data.get('organizationId', '')}. Estimated price: {data.get('estimatedPrice', 'N/A')}."
        # notifications.append(notification_text)
        notifications.append({
            "text": notification_text,
            "status": data.get("status", "pending")  # Default to "pending" if status is missing
        })

    if not notifications:
        return jsonify({"message": "No new notifications"}), 200

    return jsonify({"notifications": notifications}), 200



@app.route("/submit_delivery_details", methods=["POST"])
def submit_delivery_details():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No data received"}), 400
        user_id = data.get("user_id")   # Get userId from request
        product_id = data.get("product_id") 
        noti_ref = db.collection("individualMessage")
        matching_docs = noti_ref.where("userId", "==", user_id).where("productId", "==", product_id).stream()
        for doc in matching_docs:
            doc_ref = noti_ref.document(doc.id)
            doc_ref.set({"status": "accepted"},merge=True)

        delivery_ref = db.collection("delivery_location").document()
        delivery_ref.set({
            "user_id": data.get("user_id"),
            "user_email": data.get("user_email"),
            "user_contact": data.get("user_contact"),
            "delivery_pincode": data.get("delivery_pincode"),
            "delivery_location": data.get("delivery_location"),
            "state": data.get("state"),
            "product_id":data.get("product_id"),
            "org_id":data.get("org_id"),
            "created_at": datetime.utcnow()
        })

        return jsonify({"message": "Delivery details submitted successfully!"}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Server error", "message": str(e)}), 500


@app.route("/get_organization_deliveries", methods=["POST"])
def get_organization_deliveries():
    try:
        data = request.json
        org_id = data.get("org_id")

        if not org_id:
            return jsonify({"error": "Missing organization ID"}), 400

        deliveries_ref = db.collection("delivery_location")
        query = deliveries_ref.where("org_id", "==", org_id).stream()

        deliveries = []
        for doc in query:
            delivery_data = doc.to_dict()
            deliveries.append({
                "customer_id": delivery_data.get("user_id"),
                "customer_mail": delivery_data.get("user_email"),
                "customer_contact_no": delivery_data.get("user_contact"),
                "product_id": delivery_data.get("product_id"),
                "location": delivery_data.get("delivery_location"),
                "pincode": delivery_data.get("delivery_pincode"),
                "state": delivery_data.get("state"),
                "status":delivery_data.get("status","")
            })

        return jsonify({"deliveries": deliveries}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    





# HF_API_URL = "https://api-inference.huggingface.co/models/google/gemma-2b"
HF_API_URL = os.getenv("HF_URL")
 
HF_API_TOKEN = os.getenv("HF_API_KEY")  
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    user_text = request.form.get("text")
    if not user_text:
        return jsonify({"error": "No input provided"}), 400

   
    prompt = f"""
You are an expert in e-waste sustainability.  
Analyze the query and provide a **structured disposal guide**.  

### **User Query:**  
"{user_text}"  

### **Response Format (Follow this format exactly):**  
Item Type: [Detected electronic item]  
Potential Hazards: [List potential disposal risks]  
Recycling Steps:  
1. [Step 1]  
2. [Step 2]  
3. [Step 3]  
 

### **Response:**  
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.5,  
            "top_p": 0.85,
            "repetition_penalty": 1.2  
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  
        response_data = response.json()

       
        if isinstance(response_data, list) and response_data:
            suggestion = response_data[0].get("generated_text", "No valid response.")
        elif isinstance(response_data, dict):
            suggestion = response_data.get("generated_text", "No valid response.")
        else:
            suggestion = "Unexpected response format."

        return jsonify({"suggestion": suggestion.strip()})

    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"API request failed: {str(req_err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/beforePurchase")
def beforePurchase():
    return render_template('beforePurchase.html')

@app.route("/nearestcenters")
def nearestcenters():
    return render_template('nearestcenters.html')



YOUTUBE_API_KEY = os.getenv("YT_API_KEY")
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)







CHANNEL_NAMES = ["techbar", "trakintech", "technicalguruji", "technoruhez"]

def fetch_youtube_videos(query):
    selected_videos = []

    for channel in CHANNEL_NAMES:
        modified_query = f"{query} {channel}"  

        request = youtube.search().list(
            part="snippet",
            q=modified_query,
            maxResults=2,  
            type="video",
            order="relevance"  
        )
        response = request.execute()

       
        for item in response.get("items", []):
            video_data = {
                "title": item["snippet"]["title"],
                "video_url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
            }
            selected_videos.append(video_data)

    return selected_videos

@app.route("/search", methods=["GET"])
def search_videos():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    videos = fetch_youtube_videos(query)
    return jsonify({"videos": videos}) 




@app.route("/Search", methods=["POST"])
def search():
    data = request.json
    state_name = data.get("state", "").strip().lower()

    if not state_name:
        return jsonify({"error": "State name is required"}), 400

    
    matching_row = df[df["State"].str.lower() == state_name.lower()]
    e_waste_centers = matching_row["E-Waste Collection Centers"].values[0] if not matching_row.empty else "No data found"

    
    model = genai.GenerativeModel("gemini-1.5-flash")
 
    prompt = f"""Provide a list of 5 well-known e-waste collection and recycling centers in {state_name}, India. 
If exact locations are unavailable, generate names of reputed e-waste centers based on general knowledge of India's e-waste recycling industry.  
Ensure the response is formatted in a numbered list and does not include disclaimers about real-time data limitations.
"""


    response = model.generate_content(prompt)
    gemini_response = response.text if response and response.text else "No response from AI."

    return jsonify({
        "state": state_name,
        "e_waste_centers": e_waste_centers,
        "gemini_response": gemini_response
    })




SEARCH_ENGINE_ID = os.getenv("ENGINE_ID")  

@app.route("/compare", methods=["GET", "POST"])
def compare():
    query = request.form.get("query") if request.method == "POST" else ""
    return render_template("compare.html", query=query, search_engine_id=SEARCH_ENGINE_ID)    



@app.route("/send_greenbits", methods=["POST"])
def send_greenbits():
    data = request.json
    product_id = data.get("product_id")
    customer_id = data.get("customer_id")
    org_id = data.get("org_id")
    green_bits = data.get("green_bits")

    if not (product_id and customer_id and org_id and green_bits):
        return jsonify({"message": "Missing required data"}), 400

    # Update or create entry in database

    delivery_ref = db.collection("delivery_location")

    # Query Firestore for the matching document
    matching_docs = delivery_ref.where("product_id", "==", product_id) \
                                .where("user_id", "==", customer_id) \
                                .where("org_id", "==", org_id) \
                                .stream()

    
    for doc in matching_docs:
        doc_ref = delivery_ref.document(doc.id)
        doc_ref.set({"status": "Accepted"}, merge=True)  # Add or update the status field
        

    greenbits_ref = db.collection("greenBitsDatabase").document(product_id)
    greenbits_ref.set({
        "product_id": product_id,
        "customer_id": customer_id,
        "org_id": org_id,
        "green_bits": int(green_bits),
        "received":0
    }, merge=True)

    return jsonify({"message": "GreenBits added successfully!"}), 200




# @app.route("/get_route", methods=["POST"])
# def get_route():
#     data = request.get_json()
#     source = data.get("source")
#     destination = data.get("destination")

#     if not source or not destination:
#         return jsonify({"status": "ERROR", "message": "Invalid input"})

#     directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source}&destination={destination}&key={GOOGLE_MAPS_API_KEY}&optimizeWaypoints=true"

#     response = requests.get(directions_url)
#     route_data = response.json()

#     if route_data["status"] == "OK":
#         route = route_data["routes"][0]["legs"][0]
#         optimized_route = {
#             "start_address": route["start_address"],
#             "end_address": route["end_address"],
#             "start_location": route["start_location"],
#             "end_location": route["end_location"],
#             "distance": route["distance"]["text"],
#             "duration": route["duration"]["text"],
#             "steps": [step["html_instructions"] for step in route["steps"]]
#         }
#         return jsonify({"status": "OK", "route": optimized_route})
#     else:
#         return jsonify({"status": "ERROR", "message": route_data["status"]})



@app.route("/get_route", methods=["POST"])
def get_route():
    data = request.get_json()
    source = data.get("source")
    destination = data.get("destination")

    if not source or not destination:
        return jsonify({"status": "ERROR", "message": "Invalid input"})

    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source}&destination={destination}&key={GOOGLE_MAPS_API_KEY}&optimizeWaypoints=true"

    response = requests.get(directions_url)
    route_data = response.json()

    if route_data["status"] == "OK":
        route = route_data["routes"][0]["legs"][0]
        optimized_route = {
            "start_address": route["start_address"],
            "end_address": route["end_address"],
            "start_location": route["start_location"],
            "end_location": route["end_location"],
            "distance": route["distance"]["text"],
            "duration": route["duration"]["text"],
            "steps": [step["html_instructions"] for step in route["steps"]]
        }
        return jsonify({"status": "OK", "route": optimized_route})
    else:
        return jsonify({"status": "ERROR", "message": route_data["status"]})




@app.route('/submit-review', methods=['POST'])
def submit_review():
    try:
        data = request.json  # Get JSON data from the request
        org_id = data.get("orgId")
        user_id = data.get("userId")
        message = data.get("message")
        rating = int(data.get("rating"))

        # Validate input
        if not (org_id and user_id and message and rating):
            return jsonify({"error": "Missing required fields"}), 400
        
        user_ref = db.collection("users2").where("uid", "==", user_id).stream()
        user_name = None

        for user in user_ref:
            user_data = user.to_dict()
            user_name = user_data.get("name", "Unknown")

        # Store review in Firestore under "reviews" collection
        review_ref = db.collection("reviews").add({
            "orgId": org_id,
            "userId": user_id,
            "userName": user_name,
            "message": message,
            "rating": rating
        })

        return jsonify({"success": True, "reviewId": review_ref[1].id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/get-reviews', methods=['GET'])
def get_reviews():
    try:
        org_id = request.args.get("orgId")  # Get orgId from request parameters

        if not org_id:
            return jsonify({"error": "Missing orgId"}), 400

        # Fetch reviews matching the orgId
        reviews_ref = db.collection("reviews").where("orgId", "==", org_id).stream()
        reviews = []

        for review in reviews_ref:
            review_data = review.to_dict()
            reviews.append(review_data)

        return jsonify({"success": True, "reviews": reviews}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\user\Downloads\mutualfund-452915-9cfb77a2b866.json"

# Define GCS details
BUCKET_NAME = "predict-price"
MODEL_PATH = "models/model.pkl"
ENCODER_PATH = "models/label_encoders.pkl"
LOCAL_MODEL_PATH = "price_prediction_model.pkl"
LOCAL_ENCODER_PATH = "label_encoders.pkl"

def download_file_from_gcs(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

# Download model & encoders
# download_file_from_gcs(BUCKET_NAME, MODEL_PATH, LOCAL_MODEL_PATH)
# download_file_from_gcs(BUCKET_NAME, ENCODER_PATH, LOCAL_ENCODER_PATH)

# Load model and encoders
model = joblib.load(LOCAL_MODEL_PATH)
label_encoders = joblib.load(LOCAL_ENCODER_PATH) 





# @app.route("/predict2", methods=["POST"])
# def predict2():
#     try:
#         # Get input data
#         data = request.get_json()
#         input_df = pd.DataFrame([data])

#         # Encode categorical inputs
#         for col in ["Product Type", "Condition"]:
#             if col in label_encoders:
#                 if data[col] in label_encoders[col].classes_:
#                     input_df[col] = label_encoders[col].transform([data[col]])
#                 else:
#                     return jsonify({"error": f"Unknown category '{data[col]}' for '{col}'"}), 400

#         # Predict price
#         predicted_price = model.predict(input_df)[0]

#         return jsonify({"predicted_price": round(predicted_price, 2)})
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route("/predict2", methods=["POST"])
def predict2():
    try:
        # Get input data
        data = request.get_json()
        input_df = pd.DataFrame([data])

        # Encode categorical inputs
        for col in ["Product Type", "Condition"]:
            if col in label_encoders:
                if data[col] in label_encoders[col].classes_:
                    input_df[col] = label_encoders[col].transform([data[col]])
                else:
                    return jsonify({"error": f"Unknown category '{data[col]}' for '{col}'"}), 400

        # Predict price
        predicted_price = model.predict(input_df)[0]

        return jsonify({"predicted_price": round(predicted_price, 2)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



if __name__ == '__main__':
    app.run(debug=True)
