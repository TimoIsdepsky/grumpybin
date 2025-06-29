import RPi.GPIO as GPIO
import time
import threading
import pygame
import logging
from speech import play_edge_tts

logger = logging.getLogger(__name__)
logger.level = logging.INFO

# --- Konfiguration ---
ECHO_PIN = 23       # GPIO-Pin für ECHO vom HC-SR04
SOL_PIN = 24       # GPIO für Solenoid
DIST_THRESHOLD_CM = 40  # Abstand in cm, ab dem "Person erkannt" gilt
AUDIO_FILE = 'test.mp3'
RATTLE_INTERVAL = 0.1   # Sekunden
RATTLE_PAUSE = 0.4   # Sekunden

# --- Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(SOL_PIN, GPIO.OUT)
GPIO.output(SOL_PIN, GPIO.LOW)

# --- Audio Setup ---
pygame.mixer.init()
pygame.mixer.music.set_endevent()

# --- Messung Entfernung ---


def detect_activation():
    if GPIO.input(ECHO_PIN) == 0:
        return False

    # Warte auf Echo-Ende
    if GPIO.input(ECHO_PIN) == 1:
        return True


# --- Aktionen ---
stop_event = threading.Event()


def rattle_solenoid():
    for _ in range(6):
        if stop_event.is_set():
            break
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

def trigger_actions_guarded():
    global is_active
    if not is_active:
        is_active = True
        stop_event.clear()
        def wrapped_play():
            play_edge_tts()
            rattle_solenoid()
            global is_active
            is_active = False
        threading.Thread(target=wrapped_play, daemon=True).start()


def trigger_actions():
    stop_event.clear()
    threading.Thread(target=rattle_solenoid, daemon=True).start()
    threading.Thread(target=play_audio, daemon=True).start()


def main():
    try:
        print("Starte Mülleimer mit Ultraschallsensor...")

        while True:
            activate = detect_activation()
            logger.debug(f"Aktiviere: {activate}")

            if activate:
                logger.info("👀 Person erkannt! Aktiviere Reaktion.")
                trigger_actions_guarded()
            time.sleep(0.5)

    except KeyboardInterrupt:
        logger.info("Beendet durch Benutzer.")

    finally:
        stop_event.set()
        pygame.mixer.music.stop()
        logger.info("GPIO aufgeräumt.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Starte Hauptprogramm...")
    main()
