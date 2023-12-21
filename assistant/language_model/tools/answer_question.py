
from assistant.language_model.utils import answer_prompt, render_prompt
from openai import OpenAI
from box import Box

NAME = "answer_question"

def main(
    query: str, 
    client: OpenAI,
    config: Box,
) -> str:
    """Select action."""
    system_prompt = render_prompt(
        prompt_name=NAME,
    )
    answer = answer_prompt(
        system_prompt=system_prompt,
        user_prompt=query,
        client=client,
        model=config.language_model.model,
    ).content
    
    return answer