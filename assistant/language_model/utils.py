from box import Box
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
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


def answer_prompt(
    system_prompt: str,
    user_prompt: str,
    client: OpenAI,
    model: str,
) -> ChatCompletionMessage:
    """Answer prompt."""
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
                if system_prompt
                else "You are a helpful assistant",
            },
            {"role": "user", "content": user_prompt},
        ],
    )
    return completion.choices[0].message

def render_prompt(
    prompt_name: str,
    **kwargs,
) -> str:
    """Return rendered prompt"""
    system_prompt = str(load_prompt(prompt_name).prompt)
    system_prompt_template = Template(system_prompt)
    return system_prompt_template.render(**kwargs)