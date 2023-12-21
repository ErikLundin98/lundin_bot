from box import Box
from openai import OpenAI
from dotenv import load_dotenv
import yaml
from assistant.language_model.action import run_action
from assistant.language_model.tools import select_action

import os

OPENAI_API_KEY = "OPENAI_API_KEY"
OPENAI_ORGANIZATION = "OPENAI_ORGANIZATION"

load_dotenv()

client = OpenAI(
    api_key=os.getenv(OPENAI_API_KEY),
    organization=os.getenv(OPENAI_ORGANIZATION),
)

with open("config.yaml", "r") as file:
    config = Box(yaml.safe_load(file))


query = "What year was the wheel invented?"

action, message = select_action.main(
    query=query,
    client=client,
    config=config
)
print(message)

response = run_action(
    action=action,
    query=query,
    client=client,
    config=config,
)
print(response)

