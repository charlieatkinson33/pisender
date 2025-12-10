import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import subprocess
import re

# --- Discover Pi IP address with ping check
def discover_pi_ip():
    try:
        subprocess.check_call("ping -n 1 192.168.4.1", shell=True)
        return "192.168.4.1"
    except subprocess.CalledProcessError:
        print("[Sender] Ping to Pi failed. Try connecting to VitalsPi Network, pass:vitals123")
        return None

PI_IP = discover_pi_ip()
PORT = 9999

# --- Initial values
vitals = {
    "BloodPressure": "120/80",
    "SpO2": "98%",
    "HeartRate": "75",
    "Temperature": "37.0",
    "RespiratoryRate": "18"
}

# --- Send to Pi
def send_data():
    if not PI_IP:
        messagebox.showerror("Connection Error", "Cannot reach Pi at 192.168.4.1. Try connecting to VitalsPi Network, pass:vitals123")
        return
    try:
        data = ",".join(f"{k}={v}" for k, v in vitals.items())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PI_IP, PORT))
            s.sendall(data.encode())
    except Exception as e:
        print("[Sender] Error:", e)
        messagebox.showerror("Send Error", f"Could not send data to Pi, try connecting to VitalsPi Network, pass:vitals123: {e}")

# --- GUI
root = tk.Tk()
root.title("Vitals Sender")
root.geometry("400x500")
root.configure(bg="white")

label_widgets = {}

# --- Update and Send
def update_and_send(key, new_val):
    vitals[key] = new_val
    label_widgets[key].config(text=new_val)
    send_data()

# --- Scroll/Click Editable Labels
def create_control(frame, key, color):
    label = tk.Label(frame, text=vitals[key], font=("Helvetica", 18), fg=color, bg="white", width=12)
    label.pack(pady=10)
    label_widgets[key] = label

    def increase():
        try:
            if key == "BloodPressure":
                sys, dia = map(int, vitals[key].split("/"))
                sys += 1
                dia += 1
                update_and_send(key, f"{sys}/{dia}")
            else:
                value = float(vitals[key].replace("%", ""))
                value += 1
                suffix = "%" if key == "SpO2" else ""
                update_and_send(key, f"{value:.1f}{suffix}")
        except:
            pass

    def decrease():
        try:
            if key == "BloodPressure":
                sys, dia = map(int, vitals[key].split("/"))
                sys -= 1
                dia -= 1
                update_and_send(key, f"{sys}/{dia}")
            else:
                value = float(vitals[key].replace("%", ""))
                value -= 1
                suffix = "%" if key == "SpO2" else ""
                update_and_send(key, f"{value:.1f}{suffix}")
        except:
            pass

    def edit_manual(event):
        new_val = simpledialog.askstring("Enter value", f"Set {key}:", initialvalue=vitals[key])
        if new_val:
            update_and_send(key, new_val)

    label.bind("<Button-1>", edit_manual)
    tk.Button(frame, text="▲", command=increase).pack()
    tk.Button(frame, text="▼", command=decrease).pack()

# --- Layout
colors = {
    "BloodPressure": "red",
    "SpO2": "goldenrod",
    "HeartRate": "green",
    "Temperature": "blue",
    "RespiratoryRate": "purple"
}

for key in vitals:
    f = tk.Frame(root, bg="white")
    f.pack(pady=5)
    tk.Label(f, text=key, bg="white", font=("Helvetica", 12, "bold"), fg=colors.get(key, "black")).pack()
    create_control(f, key, colors.get(key, "black"))

root.mainloop()
