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

GPIO.output(EN, GPIO.HIGH)

# ================= MOTOR CONFIG =================
STEPS_PER_REV = 200
LEADSCREW_MM_PER_REV = 8
STEPS_PER_MM = STEPS_PER_REV / LEADSCREW_MM_PER_REV

running = False
rotation_count = 0
current_profile = None
buttons = {}

# ================= AGE PROFILES =================
AGE_PROFILES = {
    "Infant": {"depth_mm": 10, "rate": 100},
    "Child":  {"depth_mm": 15, "rate": 100},
    "Teen":   {"depth_mm": 18, "rate": 100},
    "Adult":  {"depth_mm": 20, "rate": 100}
}

# ================= MOTOR FUNCTIONS =================
def step_motor(direction, steps, delay):
    global rotation_count

    GPIO.output(DIR, direction)

    for _ in range(steps):
        if not running:
            break

        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

        rotation_count += 1 / STEPS_PER_REV


def cpr_loop():
    GPIO.output(EN, GPIO.LOW)

    depth = current_profile["depth_mm"]
    rate = current_profile["rate"]

    steps = int(depth * STEPS_PER_MM)
    cycle_time = 60 / rate
    delay = max(0.002, cycle_time / (steps * 2))

    while running:
        step_motor(CW, steps, delay)
        step_motor(CCW, steps, delay)

    GPIO.output(EN, GPIO.HIGH)

# ================= UI SAFE UPDATE =================
def update_rotation_display():
    rotation_label.config(
        text=f"Motor Rotations: {rotation_count:.2f}"
    )
    if running:
        root.after(200, update_rotation_display)

# ================= UI FUNCTIONS =================
def select_profile(age):
    global current_profile

    current_profile = AGE_PROFILES[age]

    # Reset all buttons
    for key in buttons:
        buttons[key].config(bg="SystemButtonFace")

    # Highlight selected
    buttons[age].config(bg="green")

    status_label.config(text=f"Selected: {age}")


def start_cpr():
    global running, rotation_count

    if current_profile is None:
        status_label.config(text="Select age first")
        return

    if not running:
        rotation_count = 0
        running = True
        status_label.config(text="CPR RUNNING")

        update_rotation_display()

        threading.Thread(target=cpr_loop, daemon=True).start()


def stop_cpr():
    global running
    running = False
    sleep(0.1)
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
    btn = tk.Button(
        button_frame,
        text=age,
        font=("Arial", 20),
        width=10,
        height=2,
        command=lambda a=age: select_profile(a)
    )
    btn.grid(row=i//2, column=i%2, padx=20, pady=15)
    buttons[age] = btn

status_label = tk.Label(root, text="Status: READY", font=("Arial", 18))
status_label.pack(pady=10)

rotation_label = tk.Label(
    root,
    text="Motor Rotations: 0.00",
    font=("Arial", 18)
)
rotation_label.pack(pady=5)

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
