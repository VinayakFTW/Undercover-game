from enum import Enum

class SessionStatus(str, Enum):
    WAITING = "waiting"
    ROUND1 = "round1"
    ROUND2 = "round2"
    ROUND3 = "round3"
    REVEAL = "reveal"
    COMPLETE = "complete"