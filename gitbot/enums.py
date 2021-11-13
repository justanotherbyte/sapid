from enum import Enum


class IssueLockReason(Enum):
    OFF_TOPIC = "off-topic"
    TOO_HEATED = "too heated"
    RESOLVED = "resolved"
    SPAM = "spam"