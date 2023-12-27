from box import Box
import yaml
import os
from jinja2 import Template

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


def render_prompt(
    prompt_name: str,
    prompt_key: str = "prompt",
    **kwargs,
) -> str:
    """Return rendered prompt"""
    system_prompt = str(load_prompt(prompt_name)[prompt_key])
    system_prompt_template = Template(system_prompt)
    return system_prompt_template.render(**kwargs)