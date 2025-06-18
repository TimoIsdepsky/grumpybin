import RPi.GPIO as GPIO
import time
import threading
import pygame

# --- Konfiguration ---
TRIG_PIN     = 23       # GPIO-Pin für TRIG vom HC-SR04
ECHO_PIN     = 24       # GPIO-Pin für ECHO vom HC-SR04
SOL_PIN      = 17       # GPIO für Solenoid
DIST_THRESHOLD_CM = 40  # Abstand in cm, ab dem "Person erkannt" gilt
AUDIO_FILE   = 'alert.wav'
RATTLE_INTERVAL = 0.1   # Sekunden
RATTLE_PAUSE    = 0.4   # Sekunden

# --- Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(SOL_PIN, GPIO.OUT)
GPIO.output(SOL_PIN, GPIO.LOW)

# --- Audio Setup ---
pygame.mixer.init()
pygame.mixer.music.set_endevent()

# --- Messung Entfernung ---
def measure_distance():
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.05)

    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    start = time.time()
    stop = time.time()

    # Warte auf Echo-Anfang
    while GPIO.input(ECHO_PIN) == 0:
        start = time.time()

    # Warte auf Echo-Ende
    while GPIO.input(ECHO_PIN) == 1:
        stop = time.time()

    elapsed = stop - start
    distance = (elapsed * 34300) / 2  # Schallgeschwindigkeit: 343 m/s
    return distance

# --- Aktionen ---
stop_event = threading.Event()

def rattle_solenoid():
    for _ in range(6):
        if stop_event.is_set(): break
        GPIO.output(SOL_PIN, GPIO.HIGH)
        time.sleep(RATTLE_INTERVAL)
        GPIO.output(SOL_PIN, GPIO.LOW)
        time.sleep(RATTLE_PAUSE)

def play_audio():
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        if stop_event.is_set():
            pygame.mixer.music.stop()
            break
        time.sleep(0.1)

def trigger_actions():
    stop_event.clear()
    threading.Thread(target=rattle_solenoid, daemon=True).start()
    threading.Thread(target=play_audio, daemon=True).start()

# --- Hauptschleife ---
try:
    print("Starte Mülleimer mit Ultraschallsensor...")
    last_trigger_time = 0
    cooldown = 5  # Sekunden: Zeit zwischen zwei Aktivierungen

    while True:
        distance = measure_distance()
        print(f"Gemessene Distanz: {distance:.1f} cm")

        if distance < DIST_THRESHOLD_CM:
            if time.time() - last_trigger_time > cooldown:
                print("👀 Person erkannt! Aktiviere Reaktion.")
                last_trigger_time = time.time()
                trigger_actions()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Beendet durch Benutzer.")

finally:
    stop_event.set()
    pygame.mixer.music.stop()
    GPIO.cleanup()
    print("GPIO aufgeräumt.")
