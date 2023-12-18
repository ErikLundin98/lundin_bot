from box import Box
import yaml
import os

PROMPT_DIR = "assistant/language_model/tools/prompts"

def load_prompt(prompt_name: str) -> Box:
    """Load prompt with specified name."""
    with open(
        os.path.join(
            PROMPT_DIR,
            f"{prompt_name}.yaml",
        ), 
        "r",
    ) as file:
        return Box(yaml.safe_load(file))
