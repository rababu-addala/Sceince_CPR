import tkinter as tk
import threading
from time import sleep
import RPi.GPIO as GPIO

# ---------------- GPIO Setup ----------------
DIR = 20
STEP = 21
EN = 16

CW = 1
CCW = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

GPIO.output(EN, GPIO.HIGH)  # Disabled initially

motor_running = False
rotation_count = 0

# ---------------- Motor Function ----------------
def run_motor(strokes):
    global motor_running, rotation_count

    GPIO.output(EN, GPIO.LOW)  # Enable motor
    motor_running = True
    rotation_count = 0

    for i in range(strokes):
        if not motor_running:
            break

        # Forward
        GPIO.output(DIR, CW)
        for _ in range(200):
            GPIO.output(STEP, GPIO.HIGH)
            sleep(0.001)
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.001)

        # Backward
        GPIO.output(DIR, CCW)
        for _ in range(200):
            GPIO.output(STEP, GPIO.HIGH)
            sleep(0.001)
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.001)

        rotation_count += 1
        rotation_label.config(text=f"Rotations: {rotation_count}")

    GPIO.output(EN, GPIO.HIGH)  # Disable motor
    motor_running = False


def stop_motor():
    global motor_running
    motor_running = False
    GPIO.output(EN, GPIO.HIGH)


# ---------------- UI Setup ----------------
root = tk.Tk()
root.title("CPR Machine")
root.geometry("800x480")
root.configure(bg="white")

profiles = {
    "Infant": 10,
    "Child": 20,
    "Teen": 30,
    "Adult": 40
}

buttons = {}

def select_profile(name):
    strokes = profiles[name]

    # Reset all buttons to default
    for btn in buttons.values():
        btn.config(bg="lightgray")

    # Highlight selected
    buttons[name].config(bg="green")

    # Start motor in separate thread
    threading.Thread(target=run_motor, args=(strokes,), daemon=True).start()


# Create Buttons in Grid
row = 0
col = 0
for profile in profiles:
    btn = tk.Button(root,
                    text=profile,
                    width=15,
                    height=4,
                    bg="lightgray",
                    command=lambda p=profile: select_profile(p))
    btn.grid(row=row, column=col, padx=20, pady=20)
    buttons[profile] = btn

    col += 1
    if col > 1:
        col = 0
        row += 1


rotation_label = tk.Label(root,
                          text="Rotations: 0",
                          font=("Arial", 24),
                          bg="white")
rotation_label.grid(row=3, column=0, columnspan=2, pady=20)

stop_btn = tk.Button(root,
                     text="STOP",
                     bg="red",
                     fg="white",
                     width=20,
                     height=2,
                     command=stop_motor)
stop_btn.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
GPIO.cleanup()
import tkinter as tk
import threading
from time import sleep
import RPi.GPIO as GPIO

# ---------------- GPIO Setup ----------------
DIR = 20
STEP = 21
EN = 16

CW = 1
CCW = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

GPIO.output(EN, GPIO.HIGH)  # Disabled initially

motor_running = False
rotation_count = 0

# ---------------- Motor Function ----------------
def run_motor(strokes):
    global motor_running, rotation_count

    GPIO.output(EN, GPIO.LOW)  # Enable motor
    motor_running = True
    rotation_count = 0

    for i in range(strokes):
        if not motor_running:
            break

        # Forward
        GPIO.output(DIR, CW)
        for _ in range(200):
            GPIO.output(STEP, GPIO.HIGH)
            sleep(0.001)
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.001)

        # Backward
        GPIO.output(DIR, CCW)
        for _ in range(200):
            GPIO.output(STEP, GPIO.HIGH)
            sleep(0.001)
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.001)

        rotation_count += 1
        rotation_label.config(text=f"Rotations: {rotation_count}")

    GPIO.output(EN, GPIO.HIGH)  # Disable motor
    motor_running = False


def stop_motor():
    global motor_running
    motor_running = False
    GPIO.output(EN, GPIO.HIGH)


# ---------------- UI Setup ----------------
root = tk.Tk()
root.title("CPR Machine")
root.geometry("800x480")
root.configure(bg="white")

profiles = {
    "Infant": 10,
    "Child": 20,
    "Teen": 30,
    "Adult": 40
}

buttons = {}

def select_profile(name):
    strokes = profiles[name]

    # Reset all buttons to default
    for btn in buttons.values():
        btn.config(bg="lightgray")

    # Highlight selected
    buttons[name].config(bg="green")

    # Start motor in separate thread
    threading.Thread(target=run_motor, args=(strokes,), daemon=True).start()


# Create Buttons in Grid
row = 0
col = 0
for profile in profiles:
    btn = tk.Button(root,
                    text=profile,
                    width=15,
                    height=4,
                    bg="lightgray",
                    command=lambda p=profile: select_profile(p))
    btn.grid(row=row, column=col, padx=20, pady=20)
    buttons[profile] = btn

    col += 1
    if col > 1:
        col = 0
        row += 1


rotation_label = tk.Label(root,
                          text="Rotations: 0",
                          font=("Arial", 24),
                          bg="white")
rotation_label.grid(row=3, column=0, columnspan=2, pady=20)

stop_btn = tk.Button(root,
                     text="STOP",
                     bg="red",
                     fg="white",
                     width=20,
                     height=2,
                     command=stop_motor)
stop_btn.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
GPIO.cleanup()
