import warnings
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
import joblib
import numpy as np
from flask_cors import CORS
import datetime
import math

# Silence the scikit-learn feature name warning
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
CORS(app)

# Load your trained AI model
model = joblib.load('smart_brain.pkl')

# ==========================================
# 1. THE HARDWARE ENDPOINT (For the ESP32)
# ==========================================
@app.route('/sensor-data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        
        # Safe extraction for ESP32
        raw_temp = data.get('temperature')
        temp = float(raw_temp) if (raw_temp is not None and not math.isnan(float(raw_temp))) else 0.0
        
        raw_hum = data.get('humidity')
        hum = float(raw_hum) if (raw_hum is not None and not math.isnan(float(raw_hum))) else 0.0
        
        moist = float(data.get('soilMoisture', 0))
        
        # Calculate percentage (clamped between 1500 and 4095)
        clamped_moist = max(1500, min(moist, 4095))
        moist_percent = round(100 - ((clamped_moist - 1500) / (4095 - 1500) * 100), 1)
        
        # AI Logic
        input_data = np.array([[temp, hum, moist_percent]])
        prediction = int(model.predict(input_data)[0])
        msg = "Action: Watering Required" if prediction == 1 else "Normal: No Watering Needed"
            
        print(f"📡 HARDWARE DATA: Temp: {temp}C | Hum: {hum}% | Moist: {moist_percent}% -> AI: {msg}")
            
        # Log to Firebase
        doc_ref = db.collection('irrigation_logs').document()
        doc_ref.set({
            'temperature': temp,
            'humidity': hum,
            'moisture': moist_percent,
            'pump_action': prediction,
            'timestamp': datetime.datetime.now()
        })
            
        return jsonify({"status": "success", "pump_state": prediction, "message": msg}), 200
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


# ==========================================
# 2. THE LIVE DASHBOARD ENDPOINT (For your Web UI)
# ==========================================
@app.route('/live-status', methods=['GET'])
def get_live_status():
    try:
        # Fetch the most recent document from Firebase based on timestamp
        docs = db.collection('irrigation_logs').order_by(
            'timestamp', direction=firestore.Query.DESCENDING
        ).limit(1).stream()
        
        latest_data = None
        for doc in docs:
            latest_data = doc.to_dict()
            
        if latest_data:
            return jsonify({"status": "success", "data": latest_data}), 200
        else:
            return jsonify({"status": "waiting", "message": "No data from ESP32 yet"}), 200
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================
# 3. THE MANUAL ENTRY ENDPOINT (For testing via Web UI)
# ==========================================
@app.route('/manual-predict', methods=['POST'])
def manual_predict():
    try:
        # Get the manual numbers typed into the webpage/app
        data = request.get_json()
        temp = float(data.get('temperature', 0))
        hum = float(data.get('humidity', 0))
        moist_percent = float(data.get('moisture', 0))
        
        # Run the AI logic
        input_data = np.array([[temp, hum, moist_percent]])
        prediction = int(model.predict(input_data)[0])
        msg = "Action: Watering Required" if prediction == 1 else "Normal: No Watering Needed"
        
        print(f"💻 MANUAL DATA: Temp: {temp}C | Hum: {hum}% | Moist: {moist_percent}% -> AI: {msg}")
        
        # Return the result strictly to the screen, not the physical hardware
        return jsonify({
            "status": "success", 
            "prediction": prediction, 
            "message": msg,
            "inputs": {"temp": temp, "hum": hum, "moist": moist_percent}
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ==========================================
# APP RUNNER (Must be at the very bottom)
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)