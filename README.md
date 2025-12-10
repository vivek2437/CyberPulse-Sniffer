# 🛡️ CyberPulse-Sniffer - Network Security Analysis Platform

**A complete, production-ready network security analysis tool with REST API and modern web interfaces.**

---

## 👨‍💻 Project Information

| Property | Details |
|----------|---------|
| **Project Name** | CyberPulse-Sniffer |
| **Repository Owner** | vivek2437 |
| **Type** | Network Security Analysis Platform |
| **Main API Framework** | Flask (Python) |
| **Flask API File** | `api.py` (397 lines) |
| **Purpose** | PCAP analysis with ML-powered threat detection |

### Flask API (`api.py`)
The core Flask REST API that powers the entire platform:
- **Created for**: CyberPulse-Sniffer Network Security Tool
- **Technology**: Flask + CORS + Scapy + LightGBM
- **Key Features**:
  - RESTful endpoints for PCAP upload and analysis
  - ML model integration for threat detection
  - CORS enabled for cross-origin requests
  - File upload handling with validation
  - Real-time packet analysis
  - Statistical reporting
  
**All request/response handling, file processing, and threat detection logic is implemented in `api.py`.**

---

## ⚡ Quick Start (30 seconds)

### Windows Users:
```bash
# Option 1: Double-click (easiest)
start_api.bat

# Option 2: Manual
python api.py
```

### Mac/Linux Users:
```bash
python api.py
```

Then open in your browser:
```
test_frontend.html
```

---

## 🎯 What It Does

Analyzes network traffic (PCAP files) and detects:
- ✅ **Normal Traffic** - Legitimate network activity
- 🚨 **DDoS Attacks** - Denial of Service attempts
- 🔍 **Port Scans** - Network reconnaissance
- 💉 **SQL Injection** - Database attacks
- 🦠 **Malware** - Malicious software communication

---

## 📊 Features

### Backend (Flask API)
- ✅ REST API endpoints
- ✅ PCAP file upload & analysis
- ✅ Real-time threat detection
- ✅ ML-powered classification
- ✅ CORS enabled (ready for web frontends)
- ✅ Error handling & validation
- ✅ Statistical analysis

### Frontend Options

#### 1. **Web Interface** (No Installation)
- Beautiful, responsive UI
- Drag-and-drop file upload
- Real-time results display
- Threat visualization
- Just open `test_frontend.html` in your browser

#### 2. **React Component**
- Ready-to-use component
- TypeScript support
- Tailwind CSS styling
- See: `frontend_examples/AnalyzePackets.jsx`

#### 3. **Next.js Integration**
- Server-side rendering
- API routes
- Deployment ready
- See: `frontend_examples/nextjs_example.js`

#### 4. **Command-Line**
- Python scripts
- Batch processing
- See: `test_pcap.py`

---

## 📁 Project Structure

```
ml/
├── 🚀 api.py                      # Main Flask API server
├── 🌐 test_frontend.html          # Web UI (open in browser!)
├── 🤖 lightgbm_model.pkl          # ML model (pre-trained)
│
├── 📚 Documentation
│   ├── SETUP_GUIDE.md             # Complete setup guide
│   ├── API_README.md              # API documentation
│   └── README.md                  # This file
│
├── 🧪 Testing Files
│   ├── test_pcap.py               # CLI PCAP analyzer
│   ├── test_api.py                # API endpoint tester
│   └── test_arp_attack.py         # Attack simulation test
│
├── 🎨 Frontend Examples
│   ├── AnalyzePackets.jsx         # React component
│   └── nextjs_example.js          # Next.js page
│
├── 📦 Dependencies
│   ├── requirements.txt            # Python packages
│   └── start_api.bat              # Quick launcher (Windows)
│
├── 📊 Sample Data
│   ├── 2024-07-30-traffic-analysis-exercise.pcap  # Normal traffic
│   ├── realistic_mixed_attacks.pcap               # Mixed traffic
│   └── attack_samples/
│       └── arp_attack.pcap        # Attack sample
│
└── 📁 uploads/                    # Uploaded files storage
```

---

## 🚀 Usage

### Option 1: Web Interface (Easiest!)

1. **Start the API:**
   ```bash
   python api.py
   ```

2. **Open the web interface:**
   - Double-click `test_frontend.html`
   - Or open in browser: `file:///path/to/test_frontend.html`

3. **Upload and analyze:**
   - Click "Choose PCAP File"
   - Select a `.pcap` file
   - Click "Analyze Network Traffic"
   - View results!

### Option 2: Command-Line

```bash
# Analyze a PCAP file
python test_pcap.py

# Test the API
python test_api.py
```

### Option 3: API with cURL

```bash
# Health check
curl http://localhost:5000/health

# Analyze file
curl -X POST -F "file=@traffic.pcap" \
  http://localhost:5000/analyze-quick

# Get stats
curl http://localhost:5000/stats
```

### Option 4: React/Next.js App

See `frontend_examples/` for complete implementations.

---

## 🔌 API Endpoints

### `/` (GET)
API information and available endpoints.

### `/health` (GET)
Health check - verify API is running.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-12-10T12:34:56"
}
```

### `/analyze-quick` (POST)
**Upload and analyze PCAP file in one call (recommended).**

**Request:**
```
POST /analyze-quick
Content-Type: multipart/form-data
file: <PCAP file>
```

**Response:**
```json
{
  "status": "success",
  "total_packets": 11562,
  "results": {
    "Normal": 11562,
    "DDoS": 0,
    "Port Scan": 0,
    "SQL Injection": 0,
    "Malware": 0
  },
  "percentages": {
    "Normal": 100.0,
    "DDoS": 0.0,
    "Port Scan": 0.0,
    "SQL Injection": 0.0,
    "Malware": 0.0
  },
  "top_threats": [
    {
      "packet": 42,
      "type": "Port Scan",
      "confidence": 95.32,
      "summary": "Ether / IP / TCP 192.168.1.100:56234 > ..."
    }
  ],
  "timestamp": "2025-12-10T12:34:56"
}
```

### `/upload` (POST)
Upload PCAP file (use with `/analyze` endpoint).

### `/analyze` (POST)
Analyze previously uploaded file.

### `/stats` (GET)
Get server statistics and file list.

---

## 💻 Frontend Integration

### React
```javascript
import axios from 'axios';

async function analyzeFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(
    'http://localhost:5000/analyze-quick',
    formData
  );
  
  return response.data;
}
```

### Vue.js
```javascript
const analyzeFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:5000/analyze-quick', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};
```

### Vanilla JavaScript
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5000/analyze-quick', {
  method: 'POST',
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## 📦 Installation

### Prerequisites
- Python 3.7+
- PCAP files to analyze

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Or Manual Installation
```bash
pip install flask flask-cors numpy joblib scapy scikit-learn lightgbm
```

---

## ⚙️ Configuration

Edit `api.py` to customize:

```python
# File upload settings
UPLOAD_FOLDER = 'uploads'           # Where to store files
ALLOWED_EXTENSIONS = {'pcap', 'pcapng', 'cap'}  # Allowed types
MAX_FILE_SIZE = 50 * 1024 * 1024    # 50MB max size

# Server settings (at bottom of file)
app.run(
    debug=True,        # Set to False for production
    host='0.0.0.0',   # Listen on all interfaces
    port=5000         # Server port
)
```

---

## 🧪 Testing

### Test the API
```bash
python test_api.py
```

### Analyze PCAP files
```bash
python test_pcap.py
```

### Test attack detection
```bash
python test_arp_attack.py
```

---

## 🔐 Security

### Development Mode ⚠️
- Debug enabled
- CORS open to all
- No authentication
- File size: 50MB max

### Production Deployment
1. **Disable debug mode**
   ```python
   app.run(debug=False)
   ```

2. **Use production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn api:app
   ```

3. **Restrict CORS**
   ```python
   CORS(app, resources={
       r"/api/*": {"origins": "yourdomain.com"}
   })
   ```

4. **Add authentication**
   ```bash
   pip install flask-httpauth
   ```

5. **Use HTTPS/SSL**
   - Get certificate from Let's Encrypt
   - Configure Nginx as reverse proxy

6. **Rate limiting**
   ```bash
   pip install flask-limiter
   ```

---

## 📊 Sample PCAP Files

### Included Files
- `2024-07-30-traffic-analysis-exercise.pcap` - Normal network traffic
- `realistic_mixed_attacks.pcap` - Mixed normal + attack traffic
- `attack_samples/arp_attack.pcap` - ARP spoofing attack

### Download More Files
- **Malware Traffic Analysis**: https://www.malware-traffic-analysis.net/
- **CICIDS2017 Dataset**: https://www.unb.ca/cic/datasets/ids-2017.html
- **NETRESEC Captures**: https://www.netresec.com/?page=PCAPs
- **Wireshark Samples**: https://wiki.wireshark.org/SampleCaptures

---

## 🐛 Troubleshooting

### Port 5000 Already in Use
```bash
# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux: Find and kill process
lsof -i :5000
kill -9 <PID>
```

### Model File Not Found
```bash
# Make sure lightgbm_model.pkl is in same directory as api.py
ls lightgbm_model.pkl

# Check current directory
pwd
```

### PCAP Upload Fails
- File must be `.pcap`, `.pcapng`, or `.cap`
- File size < 50MB
- File is readable (check permissions)

### API Connection Refused
- Start API server first: `python api.py`
- Check port 5000 is open
- Verify firewall settings

---

## 📈 Performance

- **Speed**: ~1000 packets/second
- **Accuracy**: Based on training data
- **Memory**: ~500MB for 50MB PCAP
- **Concurrent uploads**: Limited by system resources

### For Large Files
- Process in batches
- Use background tasks (Celery)
- Deploy on high-memory server

---

## 🚀 Deployment Options

### Heroku (Free)
```bash
# Create Procfile
echo "web: gunicorn api:app" > Procfile

# Deploy
heroku login
heroku create
git push heroku main
```

### AWS EC2
```bash
# Install and run
sudo apt update
sudo apt install python3 python3-pip
pip3 install -r requirements.txt
gunicorn api:app --bind 0.0.0.0:5000
```

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "api:app"]
```

### Google Cloud Run
```bash
gcloud run deploy cyberpulse --source .
```

---

## 📚 Documentation

- **API Details**: See `API_README.md`
- **Setup Guide**: See `SETUP_GUIDE.md`
- **Examples**: See `frontend_examples/`

---

## 🎯 Next Steps

1. **Start using it now:**
   ```bash
   python api.py
   ```
   Then open `test_frontend.html`

2. **Build a custom frontend:**
   - Use React component from `frontend_examples/`
   - Integrate with your web app

3. **Deploy to production:**
   - Follow production setup guide
   - Use Gunicorn/Nginx
   - Enable HTTPS

4. **Improve detection:**
   - Train with more data
   - Tune ML model parameters
   - Add more attack types

---

## 📞 Support

### Common Issues

**Q: How do I use this with my React app?**
A: Copy the code from `frontend_examples/AnalyzePackets.jsx` or use the React component directly.

**Q: Can I deploy this to the cloud?**
A: Yes! See deployment options above. Heroku is easiest for quick deployment.

**Q: How accurate is the detection?**
A: Accuracy depends on training data. Current model is trained on standard datasets.

**Q: Can I analyze live traffic?**
A: Currently PCAP files only. For live traffic, modify to use Scapy's `sniff()` function.

---

## 📜 License

Network security analysis tool. Use responsibly for authorized testing only.

---

## ✨ Features Summary

✅ Flask REST API  
✅ Web UI (no dependencies)  
✅ React component  
✅ Next.js compatible  
✅ ML-powered detection  
✅ PCAP analysis  
✅ Real-time results  
✅ Production-ready  
✅ Cloud deployment ready  
✅ Open CORS (develop/test)  

---

## 🎉 You're Ready!

1. Start the API: `python api.py`
2. Open the web UI: `test_frontend.html`
3. Upload a PCAP file
4. Analyze network traffic!

**Happy analyzing!** 🛡️🚀

---

**Created with ❤️ for network security professionals and learners.**
