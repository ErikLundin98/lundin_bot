
from assistant.language_model.model import LanguageModel
from assistant.language_model.utils import render_prompt
from box import Box

NAME = "answer_question"

def main(
    query: str, 
    llm: LanguageModel,
    config: Box,
) -> str:
    """Answer random user question using LLM."""
    system_prompt = render_prompt(
        prompt_name=NAME,
    )
    answer = llm.answer_prompt(
        system_prompt=system_prompt,
        user_prompt=query,
        config=config,
    ).content
    
    return answer