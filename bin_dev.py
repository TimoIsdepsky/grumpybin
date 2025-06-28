import time
import threading
import pygame
import logging
from speech import play_line

logger = logging.getLogger(__name__)

# --- Audio Setup ---
pygame.mixer.init()
pygame.mixer.music.set_endevent()

# --- Aktionen ---
stop_event = threading.Event()

def detect_activation():
    return pygame.key.get_pressed()[pygame.K_k]

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
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starte Hauptprogramm...")
    main()
