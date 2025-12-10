"""
Flask API for CyberPulse-Sniffer Network Security Tool
Provides REST API endpoints for PCAP analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import warnings
import os
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, conf
from werkzeug.utils import secure_filename
import json
from datetime import datetime

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'
conf.verb = 0

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pcap', 'pcapng', 'cap'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Load the trained LightGBM model
try:
    model = joblib.load("lightgbm_model.pkl")
    print("✓ Model loaded successfully!")
except FileNotFoundError:
    print("✗ Error: Model file 'lightgbm_model.pkl' not found")
    exit()

# Attack types mapping
ATTACK_TYPES = {
    0: "Normal",
    1: "DDoS",
    2: "Port Scan",
    3: "SQL Injection",
    4: "Malware"
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_features(packet):
    """Extract features from a packet to create a 78-feature vector"""
    features = np.zeros(78)
    features[0] = len(packet)

    if IP in packet:
        features[1] = packet[IP].proto
        features[2] = packet[IP].ttl

    if TCP in packet:
        features[3] = packet[TCP].sport
        features[4] = packet[TCP].dport
    elif UDP in packet:
        features[3] = packet[UDP].sport
        features[4] = packet[UDP].dport

    if ICMP in packet:
        features[5] = 1

    return features.reshape(1, -1)

def analyze_packet(packet):
    """Analyze a single packet and return prediction"""
    try:
        features = extract_features(packet)
        probabilities = model.predict_proba(features)[0]
        prediction = np.argmax(probabilities)
        confidence = float(probabilities[prediction] * 100)
        
        return {
            "prediction": ATTACK_TYPES.get(prediction, "Unknown"),
            "prediction_id": int(prediction),
            "confidence": round(confidence, 2),
            "probabilities": {
                ATTACK_TYPES[i]: round(float(probabilities[i] * 100), 2) 
                for i in range(len(probabilities))
            },
            "summary": packet.summary()
        }
    except Exception as e:
        return {
            "error": str(e),
            "summary": packet.summary()
        }

# ==================== API ENDPOINTS ====================

@app.route('/')
def home():
    """API information endpoint"""
    return jsonify({
        "name": "CyberPulse-Sniffer API",
        "version": "1.0.0",
        "description": "Network Security Analysis API for PCAP files",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "POST /upload": "Upload PCAP file for analysis",
            "POST /analyze": "Analyze uploaded PCAP file",
            "GET /stats": "Get analysis statistics"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a PCAP file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: pcap, pcapng, cap"}), 400
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    file.save(filepath)
    
    return jsonify({
        "message": "File uploaded successfully",
        "filename": filename,
        "filepath": filepath
    }), 200

@app.route('/analyze', methods=['POST'])
def analyze_pcap():
    """Analyze a PCAP file"""
    data = request.get_json()
    
    if not data or 'filename' not in data:
        # Try to get filename from form data
        if 'file' in request.files:
            # Handle direct file upload and analysis
            file = request.files['file']
            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({"error": "Invalid file"}), 400
            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            return jsonify({"error": "No filename provided"}), 400
    else:
        filename = data['filename']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    try:
        # Read PCAP file
        packets = rdpcap(filepath)
        total_packets = len(packets)
        
        # Analyze packets
        results = {
            "Normal": 0,
            "DDoS": 0,
            "Port Scan": 0,
            "SQL Injection": 0,
            "Malware": 0
        }
        
        packet_details = []
        threat_packets = []
        
        max_details = data.get('max_details', 100) if data else 100
        
        for i, packet in enumerate(packets):
            analysis = analyze_packet(packet)
            
            if 'error' not in analysis:
                prediction = analysis['prediction']
                results[prediction] += 1
                
                # Store detailed info for first packets or threats
                if i < max_details or prediction != "Normal":
                    packet_info = {
                        "packet_number": i + 1,
                        "prediction": prediction,
                        "confidence": analysis['confidence'],
                        "summary": analysis['summary'][:100]
                    }
                    packet_details.append(packet_info)
                    
                    if prediction != "Normal":
                        threat_packets.append({
                            **packet_info,
                            "probabilities": analysis['probabilities']
                        })
        
        # Calculate percentages
        percentages = {
            attack_type: round((count / total_packets) * 100, 2)
            for attack_type, count in results.items()
        }
        
        # Prepare response
        response = {
            "status": "success",
            "filename": filename,
            "total_packets": total_packets,
            "summary": {
                "counts": results,
                "percentages": percentages
            },
            "threats_detected": sum(results[k] for k in results if k != "Normal"),
            "threat_packets": threat_packets[:50],  # Top 50 threats
            "packet_details": packet_details[:100],  # First 100 packets
            "analysis_time": datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/analyze-quick', methods=['POST'])
def analyze_quick():
    """Quick analysis - just upload and get results in one call"""
    print(f"\n{'='*60}")
    print(f"[ANALYZE-QUICK] Request received at {datetime.now().strftime('%H:%M:%S')}")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    print(f"[ANALYZE-QUICK] File: {file.filename}, Size: {len(file.read())} bytes")
    file.seek(0)  # Reset file pointer after reading size
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400
    
    try:
        # Save temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"[ANALYZE-QUICK] Saving to: {filepath}")
        # Save file
        file.save(filepath)
        
        # Add small delay to ensure file is written
        import time
        time.sleep(0.5)
        
        # Verify file was saved
        if not os.path.exists(filepath):
            print(f"[ANALYZE-QUICK] ERROR: File not saved!")
            return jsonify({"error": "File save failed"}), 500
        
        file_size = os.path.getsize(filepath)
        print(f"[ANALYZE-QUICK] File saved successfully. Size: {file_size} bytes")
        
        # Analyze
        try:
            print(f"[ANALYZE-QUICK] Reading PCAP with Scapy...")
            packets = rdpcap(filepath)
            print(f"[ANALYZE-QUICK] Successfully read {len(packets)} packets")
        except Exception as e:
            print(f"[ANALYZE-QUICK] ERROR reading PCAP: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Failed to read PCAP: {str(e)}"}), 400
        
        total_packets = len(packets)
        print(f"[ANALYZE-QUICK] Starting analysis of {total_packets} packets...")
        
        results = {attack: 0 for attack in ATTACK_TYPES.values()}
        threats = []
        packets_analyzed = 0
        packets_failed = 0
        
        for i, packet in enumerate(packets):
            try:
                analysis = analyze_packet(packet)
                if 'error' not in analysis:
                    prediction = analysis['prediction']
                    results[prediction] += 1
                    packets_analyzed += 1
                    
                    if prediction != "Normal" and len(threats) < 20:
                        threats.append({
                            "packet": i + 1,
                            "type": prediction,
                            "confidence": analysis['confidence'],
                            "summary": analysis['summary'][:80]
                        })
                else:
                    packets_failed += 1
            except Exception as e:
                packets_failed += 1
                # Skip packets that can't be analyzed
                pass
        
        print(f"[ANALYZE-QUICK] Analysis complete: {packets_analyzed} analyzed, {packets_failed} failed")
        
        percentages = {k: round((v/total_packets)*100, 2) for k, v in results.items()}
        
        print(f"[ANALYZE-QUICK] Results: {results}")
        print(f"[ANALYZE-QUICK] Returning successful response")
        print(f"{'='*60}\n")
        
        return jsonify({
            "status": "success",
            "total_packets": total_packets,
            "results": results,
            "percentages": percentages,
            "top_threats": threats,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        import traceback
        print(f"[ANALYZE-QUICK] ERROR: {str(e)}")
        print(traceback.format_exc())
        print(f"{'='*60}\n")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get server statistics"""
    upload_files = os.listdir(app.config['UPLOAD_FOLDER'])
    pcap_files = [f for f in upload_files if allowed_file(f)]
    
    return jsonify({
        "total_files_uploaded": len(pcap_files),
        "recent_files": pcap_files[-10:] if pcap_files else [],
        "model_info": {
            "loaded": model is not None,
            "attack_types": ATTACK_TYPES
        }
    })

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 50MB"}), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 CyberPulse-Sniffer API Server")
    print("="*80)
    print("✓ Model loaded successfully")
    print("✓ Server starting on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /            - API information")
    print("  GET  /health      - Health check")
    print("  POST /upload      - Upload PCAP file")
    print("  POST /analyze     - Analyze uploaded file")
    print("  POST /analyze-quick - Upload and analyze in one call")
    print("  GET  /stats       - Get statistics")
    print("\nReady to accept requests!")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
