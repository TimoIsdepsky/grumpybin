from dataclasses import dataclass
from enum import Enum
import json

class MessageMethod(Enum):
    ADD = "ADD"
    EDIT = "EDIT"
    DELETE = "DELETE"
    GET = "GET"
    NONE = "NONE"

class MessageStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    NONE = "NONE"

class MessageType(Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    NONE = "NONE"

@dataclass
class Message:
    line: str = ""
    key: int = -1
    type: MessageType = MessageType.NONE
    status: MessageStatus = MessageStatus.NONE
    method: MessageMethod = MessageMethod.NONE

    def __str__(self):
        return f"{self.type.value}: ({self.method}, {self.line})"
    
    def to_json(self):
        return json.dumps({
            "type": self.type.value,
            "line": self.line,
            "key": self.key,
            "status": self.status.value,
            "method": self.method.value
        })

