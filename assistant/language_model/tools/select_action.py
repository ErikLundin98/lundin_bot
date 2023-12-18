from assistant.language_model.utils import load_prompt
from assistant.language_model.tools import Action
NAME = "select_action"
ACTIONS = "actions"

def main(query: str) -> Action:
    """Select action."""
    prompt = load_prompt(NAME).prompt
    actions = load_prompt(ACTIONS)
    prompt = prompt.format(
        actions=actions
    )
    print(prompt)
    return Action.ASK_QUESTION