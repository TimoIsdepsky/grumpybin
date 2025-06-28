# GrumpyBin

Code für das  Grumpybin Gruppenprojekt.

Zum installieren klone das Repository und führe 

```bash
sudo ./install.sh
```

auf dem Raspberry Pi aus.

## Bibliotheken
|Bibliothek|Zweck|Herkunft|
|---|---|---|
|os|Zugriff auf Umgebungsvariablen|Python|
|logging|Logger|Python|
|json|Interpretation von JSON Daten|Python|
|random|Zufallswahl, welcher Satz gewählt wird|Python|
|time|Zeitkontrolle des Solenoid|Python|
|threading|Parallelisierung des abspielens von Audio|Python|
|RPi.GPIO|Nutzung der GPIO pins für Sensor und Solenoid|Extern|
|pygame|Verbindung zum Audiotreiber|Extern|
|pyttsx3|Text to Speech Bibliothek zum abspielen von Audio|Extern|
|paho-mqtt|MQTT Client zum Abhören des MQTT Brokers|Extern|
