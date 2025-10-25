"""
API Server for ESP32 Wireless Data Reception
This Flask server receives vital sign data from ESP32 over WiFi
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import threading
import queue

app = Flask(__name__)
CORS(app)

# Thread-safe queue to store incoming vital data
vital_data_queue = queue.Queue(maxsize=100)

latest_vitals = {
    'heart_rate': 0,
    'blood_pressure_systolic': 0,
    'blood_pressure_diastolic': 0,
    'temperature': 0.0,
    'oxygen_saturation': 0,
    'respiratory_rate': 0,
    'ecg_value': 0,
    'ecg_leads_connected': False,
    'timestamp': None,
    'device_id': None
}

# Data history for analytics (last 1000 readings)
data_history = []
MAX_HISTORY = 1000


@app.route('/')
def home():
    """ endpoint to check if API is running"""
    return jsonify({
        'status': 'online',
        'message': 'HealthCareKit API Server is running',
        'version': '1.0',
        'endpoints': {
            '/api/vitals': 'POST - Receive vital data from ESP32',
            '/api/vitals/latest': 'GET - Get latest vital readings',
            '/api/vitals/history': 'GET - Get historical data',
            '/api/status': 'GET - Check server status'
        }
    })


@app.route('/api/vitals', methods=['POST'])
def receive_vitals():
    """Receive vital sign data from ESP32"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        vital_data = {
            'heart_rate': data.get('hr', 0),
            'blood_pressure_systolic': data.get('bp_sys', 0),
            'blood_pressure_diastolic': data.get('bp_dia', 0),
            'temperature': float(data.get('temp', 0)),
            'oxygen_saturation': data.get('spo2', 0),
            'respiratory_rate': data.get('rr', 0),
            'ecg_value': data.get('ecg', 0),
            'ecg_leads_connected': data.get('ecg_leads', False),
            'timestamp': datetime.now().isoformat(),
            'device_id': data.get('device_id', 'Unknown'),
            'sensors': data.get('sensors', {})
        }
        
        global latest_vitals
        latest_vitals = vital_data
        
        try:
            vital_data_queue.put_nowait(vital_data)
        except queue.Full:
            vital_data_queue.get()
            vital_data_queue.put(vital_data)
        
        data_history.append(vital_data)
        if len(data_history) > MAX_HISTORY:
            data_history.pop(0)
        
        ecg_status = "Connected" if vital_data['ecg_leads_connected'] else "Disconnected"
        print(f"📡 Received data from {vital_data['device_id']}: "
              f"HR={vital_data['heart_rate']} "
              f"BP={vital_data['blood_pressure_systolic']}/{vital_data['blood_pressure_diastolic']} "
              f"Temp={vital_data['temperature']}°C "
              f"SpO2={vital_data['oxygen_saturation']}% "
              f"RR={vital_data['respiratory_rate']} "
              f"ECG={vital_data['ecg_value']} ({ecg_status})")
        
        return jsonify({
            'status': 'success',
            'message': 'Vital data received successfully',
            'timestamp': vital_data['timestamp']
        }), 200
        
    except Exception as e:
        print(f"❌ Error receiving data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/vitals/latest', methods=['GET'])
def get_latest_vitals():
    """Get the most recent vital sign readings"""
    if latest_vitals['timestamp'] is None:
        return jsonify({
            'status': 'no_data',
            'message': 'No vital data received yet'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': latest_vitals
    }), 200


@app.route('/api/vitals/history', methods=['GET'])
def get_vital_history():
    """Get historical vital sign data"""
    limit = request.args.get('limit', default=100, type=int)
    limit = min(limit, MAX_HISTORY)
    
    return jsonify({
        'status': 'success',
        'count': len(data_history),
        'data': data_history[-limit:]
    }), 200


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status and statistics"""
    return jsonify({
        'status': 'online',
        'total_readings': len(data_history),
        'queue_size': vital_data_queue.qsize(),
        'latest_reading_time': latest_vitals.get('timestamp'),
        'device_id': latest_vitals.get('device_id')
    }), 200


def process_vital_data_queue():
    """Background thread to process vital data from queue"""
    while True:
        try:
            vital_data = vital_data_queue.get(timeout=1)
            vital_data_queue.task_done()
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error processing queue: {str(e)}")


def get_latest_vital_data():
    """
    Function to get latest vital data for integration with Streamlit app
    Call this from your ESP32 interface
    """
    return latest_vitals.copy()


def get_ecg_stream():
    """
    Get ECG data stream for real-time visualization
    Returns latest ECG value and connection status
    """
    return {
        'ecg_value': latest_vitals.get('ecg_value', 0),
        'ecg_leads_connected': latest_vitals.get('ecg_leads_connected', False),
        'timestamp': latest_vitals.get('timestamp')
    }


if __name__ == '__main__':
    print("=" * 60)
    print("HealthCareKit API Server")
    print("=" * 60)
    print()
    print("🚀 Starting API server...")
    print("📡 ESP32 devices can send data to: http://YOUR_IP:5000/api/vitals")
    print()
    print("To find your IP address:")
    print("  Windows: Run 'ipconfig' in Command Prompt")
    print("  Look for 'IPv4 Address' under your WiFi adapter")
    print()
    print("=" * 60)
    
    processing_thread = threading.Thread(target=process_vital_data_queue, daemon=True)
    processing_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
