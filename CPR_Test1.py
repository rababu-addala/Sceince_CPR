import tkinter as tk
import threading
from time import sleep
import RPi.GPIO as GPIO

# ---------------- GPIO SETUP ----------------
DIR = 20
STEP = 21
EN = 16

CW = 1
CCW = 0
SPR = 200  # steps per revolution (1.8° motor)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

GPIO.output(EN, GPIO.HIGH)  # disable motor initially

# ---------------- GLOBALS ----------------
motor_running = False
rotation_count = 0
selected_profile = None
motor_thread = None

# Profile -> strokes (you can tune these)
profiles = {
    "Infant": 10,
    "Child": 20,
    "Teen": 30,
    "Adult": 40
}

buttons = {}

# ---------------- MOTOR LOGIC ----------------
def update_rotation_label():
    rotation_label.config(text=f"Rotations: {rotation_count}")

def run_motor(strokes: int):
    global motor_running, rotation_count

    GPIO.output(EN, GPIO.LOW)  # enable driver
    rotation_count = 0
    root.after(0, update_rotation_label)

    # Safe delay for Pi + Python sleep()
    delay = 0.001  # adjust to 0.002 if you see vibration

    for _ in range(strokes):
        if not motor_running:
            break

        # Forward rotation
        GPIO.output(DIR, CW)
        for _ in range(SPR):
            if not motor_running:
                break
            GPIO.output(STEP, GPIO.HIGH)
            sleep(delay)
            GPIO.output(STEP, GPIO.LOW)
            sleep(delay)

        # Backward rotation
        GPIO.output(DIR, CCW)
        for _ in range(SPR):
            if not motor_running:
                break
            GPIO.output(STEP, GPIO.HIGH)
            sleep(delay)
            GPIO.output(STEP, GPIO.LOW)
            sleep(delay)

        rotation_count += 1
        root.after(0, update_rotation_label)

    GPIO.output(EN, GPIO.HIGH)  # disable driver
    motor_running = False


def start_motor():
    global motor_running, motor_thread

    if selected_profile is None:
        status_label.config(text="Status: Select a profile first")
        return

    if motor_running:
        status_label.config(text="Status: Already running")
        return

    strokes = profiles[selected_profile]
    motor_running = True
    status_label.config(text=f"Status: RUNNING ({selected_profile})")

    motor_thread = threading.Thread(target=run_motor, args=(strokes,), daemon=True)
    motor_thread.start()


def stop_motor():
    global motor_running
    motor_running = False
    GPIO.output(EN, GPIO.HIGH)  # torque release
    status_label.config(text="Status: STOPPED")


def exit_program(event=None):
    stop_motor()
    GPIO.cleanup()
    root.destroy()

# ---------------- UI LOGIC ----------------
def select_profile(name: str):
    global selected_profile
    selected_profile = name

    # Reset all button colors
    for btn in buttons.values():
        btn.config(bg="lightgray", activebackground="lightgray")

    # Highlight selected profile
    buttons[name].config(bg="green", activebackground="green")
    status_label.config(text=f"Status: Selected {name}")

# ---------------- UI SETUP ----------------
root = tk.Tk()
root.title("CPR Training Demo")
root.geometry("800x480")
root.configure(bg="white")
root.resizable(False, False)

# Center main frame
main_frame = tk.Frame(root, bg="white")
main_frame.place(relx=0.5, rely=0.5, anchor="center")

# Title
title_label = tk.Label(
    main_frame,
    text="CPR TRAINING DEMO",
    font=("Arial", 26, "bold"),
    bg="white"
)
title_label.pack(pady=(10, 2))

# Disclaimer (added back)
disclaimer_label = tk.Label(
    main_frame,
    text="For Educational Demonstration Only – Not for Medical Use",
    font=("Arial", 12),
    fg="red",
    bg="white"
)
disclaimer_label.pack(pady=(0, 10))

# Profile buttons grid
profile_frame = tk.Frame(main_frame, bg="white")
profile_frame.pack(pady=10)

row = col = 0
for profile in profiles:
    btn = tk.Button(
        profile_frame,
        text=profile,
        font=("Arial", 18),
        width=10,
        height=3,
        bg="lightgray",
        activebackground="lightgray",
        command=lambda p=profile: select_profile(p)
    )
    btn.grid(row=row, column=col, padx=20, pady=15)
    buttons[profile] = btn

    col += 1
    if col > 1:
        col = 0
        row += 1

# Rotation display
rotation_label = tk.Label(
    main_frame,
    text="Rotations: 0",
    font=("Arial", 22),
    bg="white"
)
rotation_label.pack(pady=(10, 5))

# Status display
status_label = tk.Label(
    main_frame,
    text="Status: READY",
    font=("Arial", 16),
    bg="white"
)
status_label.pack(pady=(0, 10))

# Control buttons
control_frame = tk.Frame(main_frame, bg="white")
control_frame.pack(pady=10)

start_btn = tk.Button(
    control_frame,
    text="START",
    font=("Arial", 16),
    bg="blue",
    fg="white",
    width=10,
    height=2,
    command=start_motor
)
start_btn.grid(row=0, column=0, padx=15)

stop_btn = tk.Button(
    control_frame,
    text="STOP",
    font=("Arial", 16),
    bg="red",
    fg="white",
    width=10,
    height=2,
    command=stop_motor
)
stop_btn.grid(row=0, column=1, padx=15)

exit_btn = tk.Button(
    control_frame,
    text="EXIT",
    font=("Arial", 16),
    bg="black",
    fg="white",
    width=10,
    height=2,
    command=exit_program
)
exit_btn.grid(row=0, column=2, padx=15)

# Keyboard shortcuts
root.bind("<Escape>", exit_program)           # ESC exits
root.bind("s", lambda e: stop_motor())        # 's' stops
root.bind("<Return>", lambda e: start_motor())# Enter starts

root.protocol("WM_DELETE_WINDOW", exit_program)
root.mainloop()
