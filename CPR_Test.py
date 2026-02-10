import tkinter as tk
from time import sleep
import threading
import RPi.GPIO as GPIO

# ================= GPIO SETUP =================
DIR = 20
STEP = 21
EN = 16

CW = GPIO.HIGH
CCW = GPIO.LOW

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

GPIO.output(EN, GPIO.HIGH)  # Motor disabled initially

# ================= MOTOR CONFIG =================
STEPS_PER_REV = 200
LEADSCREW_MM_PER_REV = 8
STEPS_PER_MM = STEPS_PER_REV / LEADSCREW_MM_PER_REV

running = False

# ================= AGE PROFILES (AI LOGIC) =================
AGE_PROFILES = {
    "Infant": {"depth_mm": 40, "rate": 110},
    "Child":  {"depth_mm": 50, "rate": 110},
    "Teen":   {"depth_mm": 55, "rate": 110},
    "Adult":  {"depth_mm": 60, "rate": 110}
}

current_profile = None

# ================= MOTOR FUNCTIONS =================
def step_motor(direction, steps, delay):
    GPIO.output(DIR, direction)
    for _ in range(steps):
        if not running:
            break
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

def cpr_loop():
    GPIO.output(EN, GPIO.LOW)  # Enable motor

    depth = current_profile["depth_mm"]
    rate = current_profile["rate"]

    steps = int(depth * STEPS_PER_MM)
    cycle_time = 60 / rate
    delay = cycle_time / (steps * 2)

    while running:
        step_motor(CW, steps, delay)    # Compress
        step_motor(CCW, steps, delay)   # Release

    GPIO.output(EN, GPIO.HIGH)  # Disable motor

# ================= UI CONTROL FUNCTIONS =================
def select_profile(age):
    global current_profile
    current_profile = AGE_PROFILES[age]
    status_label.config(text=f"Selected: {age}")

def start_cpr():
    global running
    if current_profile is None:
        status_label.config(text="Select age group first")
        return

    if not running:
        running = True
        status_label.config(text="CPR RUNNING")
        threading.Thread(target=cpr_loop, daemon=True).start()

def stop_cpr():
    global running
    running = False
    GPIO.output(EN, GPIO.HIGH)
    status_label.config(text="STOPPED")

def on_close():
    stop_cpr()
    GPIO.cleanup()
    root.destroy()

# ================= UI SETUP =================
root = tk.Tk()
root.title("CPR Training Demo")
root.attributes("-fullscreen", True)

# ESC key exits app
root.bind("<Escape>", lambda e: on_close())

tk.Label(
    root,
    text="CPR TRAINING DEMO",
    font=("Arial", 26, "bold")
).pack(pady=10)

tk.Label(
    root,
    text="Educational Demonstration Only – Not for Medical Use",
    font=("Arial", 14)
).pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

for i, age in enumerate(AGE_PROFILES):
    tk.Button(
        button_frame,
        text=age,
        font=("Arial", 20),
        width=10,
        height=2,
        command=lambda a=age: select_profile(a)
    ).grid(row=i//2, column=i%2, padx=20, pady=15)

status_label = tk.Label(
    root,
    text="Status: READY",
    font=("Arial", 18)
)
status_label.pack(pady=10)

control_frame = tk.Frame(root)
control_frame.pack(pady=20)

tk.Button(
    control_frame,
    text="START",
    font=("Arial", 20),
    width=10,
    height=2,
    bg="green",
    fg="white",
    command=start_cpr
).grid(row=0, column=0, padx=15)

tk.Button(
    control_frame,
    text="STOP",
    font=("Arial", 20),
    width=10,
    height=2,
    bg="red",
    fg="white",
    command=stop_cpr
).grid(row=0, column=1, padx=15)

tk.Button(
    control_frame,
    text="EXIT",
    font=("Arial", 18),
    width=10,
    height=2,
    bg="gray",
    command=on_close
).grid(row=0, column=2, padx=15)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
