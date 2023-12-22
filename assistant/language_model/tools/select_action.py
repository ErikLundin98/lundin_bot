import json
from assistant.language_model.model import LanguageModel
from assistant.language_model.utils import load_prompt, render_prompt
from assistant.language_model.action import Action
from box import Box

NAME = "select_action"
ACTIONS = "actions"

def main(
    query: str, 
    llm: LanguageModel,
    config: Box,
) -> tuple[Action, str]:
    """Select action."""
    system_prompt = render_prompt(
        prompt_name=NAME,
        actions = load_prompt(ACTIONS)
    )
    answer = llm.answer_prompt(
        system_prompt=system_prompt,
        user_prompt=query,
        config=config,
    ).content
    try:
        answer_dict = json.loads(answer)
    except json.JSONDecodeError as e:
        print("Error when parsing json", e)
        return Action.NO_ACTION, "I could not determine which action you want to perform"
    
    return answer_dict["action"], answer_dict["message"] 