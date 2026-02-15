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
SPR = 200

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

GPIO.output(EN, GPIO.HIGH)

motor_running = False
rotation_count = 0
selected_profile = None

# ---------------- MOTOR FUNCTION ----------------
def run_motor(strokes):
    global motor_running, rotation_count

    GPIO.output(EN, GPIO.LOW)
    motor_running = True
    rotation_count = 0

    for i in range(strokes):

        if not motor_running:
            break

        GPIO.output(DIR, CW)
        for _ in range(SPR):
            if not motor_running:
                break
            GPIO.output(STEP, GPIO.HIGH)
            sleep(0.001)
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.001)

        GPIO.output(DIR, CCW)
        for _ in range(SPR):
            if not motor_running:
                break
            GPIO.output(STEP, GPIO.HIGH)
            sleep(0.001)
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.001)

        rotation_count += 1
        root.after(0, update_rotation_label)

    GPIO.output(EN, GPIO.HIGH)
    motor_running = False


def update_rotation_label():
    rotation_label.config(text=f"Rotations: {rotation_count}")


def stop_motor():
    global motor_running
    motor_running = False
    GPIO.output(EN, GPIO.HIGH)


def exit_program(event=None):
    stop_motor()
    GPIO.cleanup()
    root.destroy()


# ---------------- UI SETUP ----------------
root = tk.Tk()
root.title("CPR Machine")
root.geometry("800x480")
root.configure(bg="white")

# Make window fullscreen centered style
root.resizable(False, False)

profiles = {
    "Infant": 10,
    "Child": 20,
    "Teen": 30,
    "Adult": 40
}

buttons = {}

# ---------------- MAIN FRAME (CENTERED) ----------------
main_frame = tk.Frame(root, bg="white")
main_frame.place(relx=0.5, rely=0.5, anchor="center")

def select_profile(name):
    global selected_profile
    selected_profile = name

    for btn in buttons.values():
        btn.config(bg="lightgray")

    buttons[name].config(bg="green")


# ---------------- PROFILE GRID ----------------
profile_frame = tk.Frame(main_frame, bg="white")
profile_frame.pack(pady=20)

row = 0
col = 0

for profile in profiles:
    btn = tk.Button(
        profile_frame,
        text=profile,
        font=("Arial", 18),
        width=10,
        height=3,
        bg="lightgray",
        command=lambda p=profile: select_profile(p)
    )
    btn.grid(row=row, column=col, padx=20, pady=20)
    buttons[profile] = btn

    col += 1
    if col > 1:
        col = 0
        row += 1


# ---------------- ROTATION LABEL ----------------
rotation_label = tk.Label(
    main_frame,
    text="Rotations: 0",
    font=("Arial", 24),
    bg="white"
)
rotation_label.pack(pady=20)


# ---------------- CONTROL BUTTONS ----------------
control_frame = tk.Frame(main_frame, bg="white")
control_frame.pack(pady=10)

def start_motor():
    if selected_profile is None:
        return

    strokes = profiles[selected_profile]

    threading.Thread(
        target=run_motor,
        args=(strokes,),
        daemon=True
    ).start()


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
start_btn.grid(row=0, column=0, padx=20)

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
stop_btn.grid(row=0, column=1, padx=20)

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
exit_btn.grid(row=0, column=2, padx=20)


# ---------------- KEYBOARD SHORTCUTS ----------------
root.bind("<Escape>", exit_program)
root.bind("s", lambda e: stop_motor())
root.bind("<Return>", lambda e: start_motor())

root.mainloop()
