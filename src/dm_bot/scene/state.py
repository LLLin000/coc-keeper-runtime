from enum import Enum


class SceneState(str, Enum):
    WAITING = "waiting"
    COLLECTING = "collecting"
    RESOLVING = "resolving"
    NARRATING = "narrating"
