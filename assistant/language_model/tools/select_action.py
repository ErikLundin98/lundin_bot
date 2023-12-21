import json
from assistant.language_model.utils import answer_prompt, load_prompt, render_prompt
from assistant.language_model.action import Action
from openai import OpenAI
from box import Box

NAME = "select_action"
ACTIONS = "actions"

def main(
    query: str, 
    client: OpenAI,
    config: Box,
) -> tuple[Action, str]:
    """Select action."""
    system_prompt = render_prompt(
        prompt_name=NAME,
        actions = load_prompt(ACTIONS)
    )
    answer = answer_prompt(
        system_prompt=system_prompt,
        user_prompt=query,
        client=client,
        model=config.language_model.model,
    ).content
    try:
        answer_dict = json.loads(answer)
    except json.JSONDecodeError as e:
        print("Error when parsing json", e)
        return Action.NO_ACTION, "I could not determine which action you want to perform"
    
    return answer_dict["action"], answer_dict["message"] 