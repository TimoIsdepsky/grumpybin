import time
import threading
import pygame
import logging
from speech import play_line

logger = logging.getLogger(__name__)

# --- Audio Setup ---
pygame.mixer.init()
pygame.mixer.music.set_endevent()
pygame.init()
display = pygame.display.set_mode((100, 100))

# --- Aktionen ---
stop_event = threading.Event()

def detect_activation():
    logger.debug("Warte auf Aktivierung...")
    events = pygame.event.get()
    logger.debug(f"Erkannte Events: {events}")
    for event in events:
        logger.debug(f"Event erkannt: {event}")
        if event.type == pygame.KEYDOWN:
            logger.debug(f"Tastendruck erkannt: {event.key}")
            if event.key == pygame.K_k:
                logger.info("Aktivierung erkannt durch Tastendruck.")
                return True

def trigger_actions():
    stop_event.clear()
    threading.Thread(target=play_line, daemon=True).start()

def main():
    try:
        print("Starte Mülleimer mit Ultraschallsensor...")

        while True:
            activate = detect_activation()
            logger.debug(f"Aktiviere: {activate}")

            if activate:
                logger.info("👀 Person erkannt! Aktiviere Reaktion.")
                trigger_actions()
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
