from enum import Enum, auto
from typing import Callable
from box import Box

from openai import OpenAI
from assistant.language_model.tools import answer_question

class Action(Enum):
    """List of actions."""
    NO_ACTION = auto()
    GET_WEATHER = auto()
    TOGGLE_LIGHT = auto()
    ANSWER_QUESTION = auto()
    TELL_JOKE = auto()

def run_action(
    action: Action,
    query: str,
    client: OpenAI,
    config: Box,
) -> str:
    """Run action."""
    match action:
        case Action.NO_ACTION.value:
            return "Sorry, I could not perform any action"
        case Action.GET_WEATHER.value:
            raise NotImplementedError()
        case Action.TOGGLE_LIGHT.value: 
            raise NotImplementedError()
        case Action.ANSWER_QUESTION.value:
            return answer_question.main(
                query=query,
                client=client,
                config=config,
            )
        case Action.TELL_JOKE.value:
            raise NotImplementedError()