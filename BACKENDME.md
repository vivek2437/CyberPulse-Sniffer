# 🔐 Network Security: Real-Time Packet Sniffer & AI Threat Detection  

A powerful real-time **network packet sniffer** combined with an **AI-powered cybersecurity threat detection system**, built using **Python**, **LightGBM**, **Scapy**, and **Tkinter**.

This system analyzes live traffic, detects malicious packets with **99.88% accuracy**, visualizes findings in a clean dashboard, and supports offline PCAP analysis.

---

# 🚀 Features

## 🔥 AI-Powered Threat Detection
- LightGBM Gradient Boosting Model  
- **99.88% accuracy** on test dataset  
- Predicts **Benign / Malicious** packets  
- Supports attack categories (DoS, Probe, DDoS, etc.)*

## 📡 Real-Time Packet Sniffing
- High-speed packet capture via **Scapy**  
- Processes packets with **< 50 ms latency**  
- Extracts features dynamically  
- Runs smoothly on low-resource machines  

## 🌐 Multi-Protocol Support
- TCP  
- UDP  
- ICMP  
- Plus custom Scapy layers  

## 🖥 GUI Dashboard (Tkinter)
- Live packet stream table  
- Threat classification + confidence  
- Dynamic Matplotlib confidence graphs  
- Start/Stop sniffing  
- Import & analyze PCAP files  

## 📁 PCAP Analysis
- Load .pcap files  
- Batch classify packets with AI  
- Export results (CSV/JSON)  

---

# 🏗 Folder Structure  

```
network-threat-detection/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── routers/
│   │   │   ├── predict.py
│   │   │   ├── pcap.py
│   │   │   ├── live.py
│   │   │   └── stats.py
│   │   │
│   │   ├── services/
│   │   │   ├── sniffer.py
│   │   │   ├── feature_engine.py
│   │   │   ├── model_loader.py
│   │   │   └── pcap_reader.py
│   │   │
│   │   ├── models/
│   │   │   └── lightgbm_model.pkl       
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py (optional)
│   │   │
│   │   ├── database/
│   │       ├── mongo.py
│   │       └── postgres.py
│   │
│   ├── requirements.txt
│
├── ml/
│   ├── notebooks/
│   │   └── training_lightgbm.ipynb       
│   │
│   ├── pipeline/
│   │   ├── preprocess.py
│   │   └── train_model.py
│   │
│   ├── saved_models/
│   │   └── lightgbm_model.pkl           
│   │
│   └── feature_list.txt
│
├── dataset/
│   ├── raw/                              
│   ├── processed/                       
│   └── example_samples/                  
│
└── BACKENDME.md

---

# ⚙️ Installation

## 1️⃣ Install Dependencies  
```
pip install numpy pandas scikit-learn joblib scapy matplotlib lightgbm
```

Or via requirements:

```
pip install -r requirements.txt
```

---

# ▶️ Usage

## 🟢 Run the GUI Application
```
python gui/main.py
```

## 🟣 Run Backend Server (optional)
_For React / Next.js API integration (future)_

```
python backend/app.py
```

---

# 🤖 Model Details  

- **Model File**: `lightgbm_model.pkl`  
- **Technique**: Gradient Boosting (LightGBM)  
- **Accuracy**: **99.88%**  
- **Supports** real-time & offline predictions  
- **Feature groups**:
  - Packet size  
  - Flags (SYN, ACK, FIN…)  
  - Protocol type  
  - Flow statistics (inter-arrival time, byte rate)  

---

# 📊 Performance

| Metric | Result |
|--------|--------|
| Accuracy | **99.88%** |
| Real-time latency | **< 50 ms** |
| CPU impact | Low |
| Protocols supported | TCP/UDP/ICMP |

### Real-Time GUI Highlights
- Live packet summary  
- Dynamic confidence graph  
- Threat-level indicators  
- Interactive PCAP analysis  

---

# 🚀 Future Improvements

### 🔗 SIEM Integration  
Forward alerts to:  
- Elastic Stack  
- Splunk  
- IBM QRadar  

### ☁ Cloud Deployment  
Convert backend into REST API  
Deploy using:  
- Docker  
- AWS EC2 / Lambda  
- GCP Cloud Run  

### 🧠 Deep Learning Models  
Upgrade to CNN-LSTM network-based IDS.

### 🛡 Auto-Mitigation (Advanced)
- Auto-block suspicious IPs  
- Drop malicious packets  
- Trigger firewall rules  

---

# 🧪 Dataset  
Not included in repo (due to size).  
Recommended sources:
- UNSW-NB15  
- CIC-IDS 2017  
- KDD99 (classic)  
- Custom packet captures (Wireshark)  

Place dataset inside:
```
training/dataset/
```

---

# 🙌 Contributing  
Pull requests welcome!  
For major changes, open an issue first.

---

# 📜 License  
MIT License (customize if needed)

---

# ⭐ Support  
If you like this project, consider starring the repository!