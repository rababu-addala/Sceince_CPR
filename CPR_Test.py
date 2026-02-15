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
SPR = 200  # Steps per revolution (1.8° motor)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

GPIO.output(EN, GPIO.HIGH)  # Motor disabled initially

motor_running = False
rotation_count = 0

# ---------------- MOTOR FUNCTION ----------------
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
        for _ in range(SPR):
            if not motor_running:
                break
            GPIO.output(STEP, GPIO.HIGH)
            sleep(0.001)
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.001)

        # Backward
        GPIO.output(DIR, CCW)
        for _ in range(SPR):
            if not motor_running:
                break
            GPIO.output(STEP, GPIO.HIGH)
            sleep(0.001)
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.001)

        rotation_count += 1

        # Safe UI update using after()
        root.after(0, update_rotation_label)

    GPIO.output(EN, GPIO.HIGH)  # Disable motor after finish
    motor_running = False


def update_rotation_label():
    rotation_label.config(text=f"Rotations: {rotation_count}")


def stop_motor():
    global motor_running
    motor_running = False
    GPIO.output(EN, GPIO.HIGH)  # Disable motor immediately


def exit_program(event=None):
    stop_motor()
    GPIO.cleanup()
    root.destroy()


# ---------------- UI SETUP ----------------
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

    # Reset all buttons
    for btn in buttons.values():
        btn.config(bg="lightgray", activebackground="lightgray")

    # Highlight selected
    buttons[name].config(bg="green", activebackground="green")

    root.update_idletasks()

    # Start motor thread
    threading.Thread(
        target=run_motor,
        args=(strokes,),
        daemon=True
    ).start()


# ---------------- CREATE PROFILE GRID ----------------
row = 0
col = 0

for profile in profiles:
    btn = tk.Button(
        root,
        text=profile,
        font=("Arial", 18),
        width=12,
        height=3,
        bg="lightgray",
        activebackground="lightgray",
        command=lambda p=profile: select_profile(p)
    )
    btn.grid(row=row, column=col, padx=20, pady=20)
    buttons[profile] = btn

    col += 1
    if col > 1:
        col = 0
        row += 1


# ---------------- ROTATION DISPLAY ----------------
rotation_label = tk.Label(
    root,
    text="Rotations: 0",
    font=("Arial", 24),
    bg="white"
)
rotation_label.grid(row=3, column=0, columnspan=2, pady=20)


# ---------------- STOP BUTTON ----------------
stop_btn = tk.Button(
    root,
    text="STOP",
    font=("Arial", 18),
    bg="red",
    fg="white",
    width=15,
    height=2,
    command=stop_motor
)
stop_btn.grid(row=4, column=0, columnspan=2, pady=10)


# ---------------- KEYBOARD SHORTCUTS ----------------
root.bind("<Escape>", exit_program)  # ESC to exit
root.bind("s", lambda event: stop_motor())  # Press S to stop


root.mainloop()
