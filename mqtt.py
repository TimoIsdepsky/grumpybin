import paho.mqtt.client as mqtt
import os
import logging
from enum import Enum
import json
from message import Message, MessageType, MessageStatus, MessageMethod
from storage import StorageBackendType, FileStorageBackend, PostgreSQLStorageBackend

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT   = os.getenv("MQTT_PORT", "1883")
MQTT_TOPIC  = os.getenv("MQTT_TOPIC", "grumpybin/lines")

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"

    @classmethod
    def from_string(cls, level_str: str):
        try:
            return cls[level_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid log level: {level_str}")
    
    def __str__(self):
        return self.value

def setup_storage_backend():
    storage_backend_type = StorageBackendType.from_string(os.getenv("STORAGE_BACKEND", "FILE"))
    if storage_backend_type == StorageBackendType.FILE:
        storage_backend = FileStorageBackend("lines")
    elif storage_backend_type == StorageBackendType.DATABASE:
        if not os.getenv("DATABASE_CONNECTION_STRING"):
            raise ValueError("DATABASE_CONNECTION_STRING environment variable is not set for DATABASE storage backend.")
        logger.info("Using PostgreSQL storage backend")
        storage_backend = PostgreSQLStorageBackend(os.getenv("DATABASE_CONNECTION_STRING", ""))
    else:
        raise ValueError(f"Unsupported storage backend: {storage_backend_type}")
    
    return storage_backend

def disambiguate(msg: Message):
    if msg.method == MessageMethod.ADD:
        line_id = storage_backend.add_line(msg.line)
        logger.info(f"Added line {line_id}: {msg.line}")
        mqtt_publish(f"{Message(type=MessageType.RESPONSE, status=MessageStatus.SUCCESS, line=str(f'Added line: {line_id}: {msg.line}'), key=line_id).to_json()}")
    elif msg.method == MessageMethod.EDIT:
        line_id = storage_backend.modify_line(msg.key, msg.line)
        mqtt_publish(f"{Message(type=MessageType.RESPONSE, status=MessageStatus.SUCCESS, line=str(f'Modified line: {line_id}: {msg.line}'), key=line_id).to_json()}")
    elif msg.method == MessageMethod.DELETE:
        line_id = storage_backend.delete_line(msg.key)
        mqtt_publish(f"{Message(type=MessageType.RESPONSE, status=MessageStatus.SUCCESS, line=str(f'Deleted line: {line_id}'), key=line_id).to_json()}")
    elif msg.method == MessageMethod.GET:
        lines = storage_backend.get_lines()
        mqtt_publish(f"{Message(type=MessageType.RESPONSE, status=MessageStatus.SUCCESS, line=str(f'Current lines: {lines}')).to_json()}")
    elif msg.method == MessageMethod.NONE:
        logger.info(f"Received message without method: {msg.line}")
        mqtt_publish(f"{Message(type=MessageType.RESPONSE, status=MessageStatus.SUCCESS, line=str(f'Received message: {msg.line}')).to_json()}")
    else:
        logger.error(f"Unknown message type: {msg.method}")

def mqtt_publish(msg: str):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, int(MQTT_PORT), 60)
    client.publish(MQTT_TOPIC, msg)
    client.disconnect()
    logger.info(f"Published message: {msg} to topic: {MQTT_TOPIC}")

def on_connect(client, userdata, flags, reason_code, properties=None):
    if flags.get('session_present', False):
        logger.info("Session is present")
    if reason_code == 0:
        logger.info(f"Connected with result code {reason_code}")
        client.subscribe(MQTT_TOPIC)
    else:
        logger.error(f"Failed to connect, return code {reason_code}")

def on_message(client, userdata, message):
    recieved = json.loads(message.payload.decode())
    logger.debug(MessageMethod[recieved.get("method", "NONE")])
    recieved = Message(
        type=MessageType[recieved.get("type", "NONE")],
        line=recieved.get("line", ""),
        status=MessageStatus[recieved.get("status", "NONE")],
        method=MessageMethod[recieved.get("method", "NONE")],
        key=recieved.get("key", -1)
    )
    logger.info(f"Received message: {recieved} on topic {message.topic}")
    try:
        if (recieved.type == MessageType.REQUEST):
            disambiguate(recieved)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        mqtt_publish(f"{Message(type=MessageType.RESPONSE, status=MessageStatus.ERROR, line=str(e)).to_json()}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    global storage_backend
    storage_backend = setup_storage_backend()
    log_level = LogLevel.from_string(os.getenv("LOG_LEVEL", "INFO"))
    logger.info(f"Log level configuration: {log_level}")
    if(log_level == LogLevel.DEBUG):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info(f"Loggin with level: {logging.getLevelName(logging.getLogger().getEffectiveLevel())}")

    logger.info("Starting MQTT client...")
    logger.info(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} on topic {MQTT_TOPIC}")

    logger.info(f"Using storage backend: {storage_backend.backend_type}")

    client.connect(MQTT_BROKER, int(MQTT_PORT), 60)

    client.loop_start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Exiting...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
