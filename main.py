import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import numpy as np
import joblib
import warnings
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

# Import Scapy with error handling
try:
    from scapy.all import sniff, rdpcap, IP, TCP, UDP, ICMP, get_if_list, conf
    conf.verb = 0  # Suppress Scapy warnings
    SCAPY_AVAILABLE = True
except Exception as e:
    SCAPY_AVAILABLE = False
    print(f"Scapy import warning (continuing anyway): {e}")

# Load the trained LightGBM model
try:
    model = joblib.load("lightgbm_model.pkl")
except FileNotFoundError:
    messagebox.showerror("Error", "Model file 'lightgbm_model.pkl' not found. Please check the file path.")
    exit()

# GUI setup
root = tk.Tk()
root.title("CyberPulse-Sniffer - Wi-Fi Network Monitoring")
root.geometry("900x600")
root.configure(bg="#1e1e1e")

# Title Label
title_label = tk.Label(root, text="CyberPulse-Sniffer - Wi-Fi Network Monitoring", font=("Helvetica", 16, "bold"), bg="#1e1e1e", fg="white")
title_label.pack(pady=10)

# Packet List Display with Scrollbar
frame = tk.Frame(root)
frame.pack(pady=10, fill="both", expand=True)

packet_list = ttk.Treeview(frame, columns=("Packet Summary", "Prediction", "Confidence"), show="headings", height=10)
packet_list.heading("Packet Summary", text="Packet Summary")
packet_list.heading("Prediction", text="Prediction")
packet_list.heading("Confidence", text="Confidence (%)")

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=packet_list.yview)
packet_list.configure(yscrollcommand=scrollbar.set)
packet_list.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Identify Wi-Fi interface with manual selection fallback
def get_wifi_interface():
    if not SCAPY_AVAILABLE:
        return None
    try:
        interfaces = get_if_list()
        wifi_interfaces = [iface for iface in interfaces if "wlan" in iface.lower() or "wifi" in iface.lower() or "wlp" in iface.lower()]
        return wifi_interfaces[0] if wifi_interfaces else None
    except:
        return None

wifi_iface = get_wifi_interface()

# Feature Extraction
def extract_features(packet):
    """ Extract features from a packet to create a 78-feature vector. """
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

# Matplotlib Figure for Confidence Graph
fig, ax = plt.subplots(figsize=(4, 2))
ax.set_title("Prediction Confidence")
ax.set_ylim([0, 200])
ax.set_ylabel("Confidence (%)")
ax.set_xticks([])
bar = ax.bar([""], [0], color="lime")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

# Process Incoming Packet
packet_data = []

def process_packet(packet):
    try:
        features = extract_features(packet)
        probabilities = model.predict_proba(features)[0]
        prediction = np.argmax(probabilities)
        confidence = probabilities[prediction] * 100

        # Attack types for display
        attack_types = {0: "Normal", 1: "DDoS", 2: "Port Scan", 3: "SQL Injection", 4: "Malware"}
        prediction_label = attack_types.get(prediction, "Unknown")

        # Store packet data
        packet_info = (packet.summary(), prediction_label, confidence)
        packet_data.append(packet_info)

        # Update GUI safely
        root.after(0, lambda: update_gui(packet_info))

        # Update confidence graph
        bar[0].set_height(confidence)
        bar[0].set_color("red" if confidence > 80 else "orange" if confidence > 50 else "lime")
        canvas.draw()

    except Exception as e:
        print(f"Error processing packet: {e}")

def update_gui(packet_info):
    """ Thread-safe method to update the GUI with new packet data """
    summary, prediction, confidence = packet_info
    packet_list.insert("", "end", values=(summary, prediction, f"{confidence:.2f}"))
    packet_list.yview_moveto(1.0)

# Sniffing Control
sniffing = False

def start_sniffing():
    global sniffing
    if not wifi_iface:
        messagebox.showerror("Error", "No Wi-Fi interface detected. Please use 'Analyze PCAP' to analyze packet files instead.")
        return

    sniffing = True
    messagebox.showinfo("Packet Sniffing", f"Started sniffing on Wi-Fi interface: {wifi_iface}")

    def sniff_packets():
        try:
            sniff(iface=wifi_iface, prn=process_packet, store=False, stop_filter=lambda x: not sniffing)
        except Exception as e:
            messagebox.showerror("Sniffing Error", f"Error while sniffing: {e}")

    sniff_thread = threading.Thread(target=sniff_packets, daemon=True)
    sniff_thread.start()

def stop_sniffing():
    global sniffing
    sniffing = False
    messagebox.showinfo("Packet Sniffing", "Stopped sniffing network packets.")

# PCAP File Analysis
def analyze_pcap():
    file_path = filedialog.askopenfilename(filetypes=[("PCAP Files", "*.pcap")])
    if file_path:
        packets = rdpcap(file_path)
        for packet in packets:
            process_packet(packet)
        messagebox.showinfo("PCAP Analysis", f"Analyzed {len(packets)} packets from {file_path}")

# Buttons
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Start Sniffing", bg="lime", command=start_sniffing)
start_button.grid(row=0, column=0, padx=10)

stop_button = tk.Button(button_frame, text="Stop Sniffing", bg="red", command=stop_sniffing)
stop_button.grid(row=0, column=1, padx=10)

pcap_button = tk.Button(button_frame, text="Analyze PCAP", bg="blue", fg="white", command=analyze_pcap)
pcap_button.grid(row=0, column=2, padx=10)

# Bring window to front
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False))

# Show startup message
print("\n" + "="*80)
print("✓ CyberPulse-Sniffer GUI Started Successfully!")
print("="*80)
print("GUI Window Title: 'CyberPulse-Sniffer - Wi-Fi Network Monitoring'")
print("\nAvailable Actions:")
print("  1. Click 'Analyze PCAP' button to test with PCAP files")
print("  2. Select your PCAP file from the file browser")
print("  3. View results in the packet list")
print("\nReady to analyze network traffic!")
print("="*80 + "\n")

# Run GUI
root.mainloop()