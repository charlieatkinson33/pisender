import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import socket
import subprocess

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

# --- Initial values (what's currently displayed on OBS)
current_display = {
    "BloodPressure": "120/80",
    "SpO2": "98%",
    "HeartRate": "75",
    "Temperature": "37.0",
    "RespiratoryRate": "18"
}

# --- New values to be sent (starts as copy of current display)
new_values = current_display.copy()

# --- Visibility state for each vital sign (True = visible, False = hidden)
visibility_state = {
    "BloodPressure": True,
    "SpO2": True,
    "HeartRate": True,
    "Temperature": True,
    "RespiratoryRate": True
}

# --- Color scheme
colors = {
    "BloodPressure": "red",
    "SpO2": "goldenrod",
    "HeartRate": "green",
    "Temperature": "blue",
    "RespiratoryRate": "purple"
}

# --- Send to Pi
def send_data():
    """Send new values to Pi and update current display (only visible ones)"""
    if not PI_IP:
        messagebox.showerror("Connection Error", "Cannot reach Pi at 192.168.4.1. Try connecting to VitalsPi Network, pass:vitals123")
        return
    try:
        # Only send visible vital signs
        visible_values = {k: v for k, v in new_values.items() if visibility_state.get(k, True)}
        data = ",".join(f"{k}={v}" for k, v in visible_values.items())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PI_IP, PORT))
            s.sendall(data.encode())
        
        # Update current display labels after successful send (only visible ones)
        for key in visible_values:
            current_display[key] = new_values[key]
            current_labels[key].config(text=current_display[key])
        
        messagebox.showinfo("Success", "It didn't break! Obs updated")
    except Exception as e:
        print("[Sender] Error:", e)
        messagebox.showerror("Send Error", f"Could not send obs, try connecting to VitalsPi Network, pass:vitals123: {e}")

# --- GUI
root = tk.Tk()
root.state('zoomed')
root.title("Charlie is a genius")
root.geometry("700x600")
root.configure(bg="#f0f0f0")

current_labels = {}
new_labels = {}
visibility_frames = {}  # Store frames for hiding/showing

# --- Update new value (does NOT send)
def update_new_value(key, new_val):
    """Update the new value to be sent (without sending)"""
    new_values[key] = new_val
    new_labels[key].config(text=new_val)

# --- Create control for editing values
def create_control(frame, key, color):
    """Create up/down buttons and click-to-edit functionality"""
    label = tk.Label(frame, text=new_values[key], font=("Helvetica", 16, "bold"), 
                     fg=color, bg="white", width=12, relief="solid", borderwidth=1, padx=5, pady=5)
    label.pack(pady=5)
    new_labels[key] = label

    def increase():
        try:
            if key == "BloodPressure":
                sys, dia = map(int, new_values[key].split("/"))
                sys += 1
                dia += 1
                update_new_value(key, f"{sys}/{dia}")
            elif key == "Temperature":
                value = float(new_values[key])
                value += 1
                update_new_value(key, f"{value:.1f}")
            else:
                value = float(new_values[key].replace("%", ""))
                value += 1
                suffix = "%" if key == "SpO2" else ""
                update_new_value(key, f"{int(value)}{suffix}")
        except (ValueError, IndexError, AttributeError):
            pass

    def decrease():
        try:
            if key == "BloodPressure":
                sys, dia = map(int, new_values[key].split("/"))
                sys -= 1
                dia -= 1
                update_new_value(key, f"{sys}/{dia}")
            elif key == "Temperature":
                value = float(new_values[key])
                value -= 1
                update_new_value(key, f"{value:.1f}")
            else:
                value = float(new_values[key].replace("%", ""))
                value -= 1
                suffix = "%" if key == "SpO2" else ""
                update_new_value(key, f"{int(value)}{suffix}")
        except (ValueError, IndexError, AttributeError):
            pass

    def edit_manual(event):
        new_val = simpledialog.askstring("Enter value", f"Set {key}:", initialvalue=new_values[key])
        if new_val:
            update_new_value(key, new_val)

    label.bind("<Button-1>", edit_manual)
    
    button_frame = tk.Frame(frame, bg="white")
    button_frame.pack()
    tk.Button(button_frame, text="▲", command=increase, width=3, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=2)
    tk.Button(button_frame, text="▼", command=decrease, width=3, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=2)

# --- Toggle visibility function
def toggle_visibility(key):
    """Toggle visibility of a vital sign on both left and right sides"""
    visibility_state[key] = not visibility_state[key]
    if visibility_state[key]:
        # Show the content frames
        visibility_frames[key].pack(pady=8, padx=10)
        visibility_frames[key + "_content"].pack(pady=8, padx=10)
    else:
        # Hide the content frames
        visibility_frames[key].pack_forget()
        visibility_frames[key + "_content"].pack_forget()

# --- Create a scrollable frame using Canvas
canvas_frame = tk.Frame(root, bg="#f0f0f0")
canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

canvas = tk.Canvas(canvas_frame, bg="#f0f0f0", highlightthickness=0)
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill=tk.BOTH, expand=True)
scrollbar.pack(side="right", fill="y")

# Enable mouse wheel scrolling
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

# --- Main container inside scrollable frame
main_container = tk.Frame(scrollable_frame, bg="#f0f0f0")
main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- Left side: Current Display
left_frame = tk.Frame(main_container, bg="white", relief="ridge", borderwidth=2)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

tk.Label(left_frame, text=" CURRENT DISPLAY (OBS)", font=("Helvetica", 14, "bold"), 
         bg="#e8f4f8", fg="#333", pady=10).pack(fill=tk.X)

for key in current_display:
    # Container frame for each vital sign (to be shown/hidden)
    container = tk.Frame(left_frame, bg="white")
    container.pack(pady=8, padx=10, fill=tk.X)
    visibility_frames[key + "_left"] = container
    
    # Toggle button
    toggle_btn = tk.Checkbutton(container, text="☑", font=("Helvetica", 10), 
                                bg="white", fg=colors.get(key, "black"),
                                selectcolor="white", indicatoron=False, width=3,
                                command=lambda k=key: toggle_visibility(k))
    toggle_btn.select()  # Start selected
    toggle_btn.pack(side=tk.TOP, anchor="ne", padx=2, pady=2)
    
    f = tk.Frame(container, bg="white")
    f.pack(pady=8, padx=10)
    tk.Label(f, text=key, bg="white", font=("Helvetica", 11, "bold"), 
             fg=colors.get(key, "black")).pack()
    
    display_label = tk.Label(f, text=current_display[key], font=("Helvetica", 16), 
                            fg=colors.get(key, "black"), bg="#f9f9f9", width=12, 
                            relief="sunken", borderwidth=1, padx=5, pady=5)
    display_label.pack(pady=3)
    current_labels[key] = display_label
    
    # Store the content frame for hiding/showing
    visibility_frames[key] = f

# --- Right side: New Values to Send
right_frame = tk.Frame(main_container, bg="white", relief="ridge", borderwidth=2)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

tk.Label(right_frame, text=" NEW VALUES (Edit Here)", font=("Helvetica", 14, "bold"), 
         bg="#fff4e6", fg="#333", pady=10).pack(fill=tk.X)

for key in new_values:
    # Container frame for each vital sign (linked to left side visibility)
    container = tk.Frame(right_frame, bg="white")
    container.pack(pady=8, padx=10, fill=tk.X)
    visibility_frames[key + "_right"] = container
    
    f = tk.Frame(container, bg="white")
    f.pack(pady=8, padx=10)
    tk.Label(f, text=key, bg="white", font=("Helvetica", 11, "bold"), 
             fg=colors.get(key, "black")).pack()
    create_control(f, key, colors.get(key, "black"))
    
    # Store the content frame for hiding/showing (links to left toggle)
    visibility_frames[key + "_content"] = f

# --- Send button at the bottom (outside scrollable area)
send_button = tk.Button(root, text="📤 SEND TO OBS", command=send_data, 
                        font=("Helvetica", 14, "bold"), bg="#4CAF50", fg="white", 
                        pady=15, cursor="hand2")
send_button.pack(fill=tk.X, padx=10, pady=10)

root.mainloop()
