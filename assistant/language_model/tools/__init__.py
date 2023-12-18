from enum import Enum, auto
from typing import Callable

class Action(Enum):
    """List of actions."""
    GET_WEATHER = auto()
    TOGGLE_LIGHT = auto()
    ASK_QUESTION = auto()
    TELL_JOKE = auto()

def get_action(action: Action) -> Callable:
    """Get action to call."""
    match action:
        case Action.GET_WEATHER:
            raise NotImplementedError()
        case Action.TOGGLE_LIGHT: 
            raise NotImplementedError()
        case Action.ASK_QUESTION:
            raise NotImplementedError()
        case Action.TELL_JOKE:
            raise NotImplementedError()