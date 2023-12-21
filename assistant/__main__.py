from dotenv import load_dotenv
import os
import yaml
from box import Box
from assistant.constants import OPENAI_API_KEY, OPENAI_ORGANIZATION
from assistant.language_model.action import run_action
from assistant.language_model.tools import select_action
from assistant.speech_to_text.model import Transcriber
from openai import OpenAI
import logging
import sys
from assistant.utils import contains_wake_word

log_ = logging.getLogger(__name__)

def main(config: Box):
    """Start voice assistant service."""
    transcriber = Transcriber(config=config)
    openai_client = OpenAI(
        api_key=os.getenv(OPENAI_API_KEY),
        organization=os.getenv(OPENAI_ORGANIZATION),
    )
    log_.info("Initialized transcriber, llm client.")
    while True:
        transcription = transcriber.get_transcription()
        if transcription:   
            log_.info(f"Got transcription {transcription}.")
        if transcription and contains_wake_word(
            sentence=transcription,
            wake_word=config.speech_to_text.wake_word,
            threshold=config.speech_to_text.similarity_score,
        ):
            log_.info("Recognized wake word.")
            action, message = select_action.main(
                query=transcription,
                client=openai_client,
                config=config
            )
            log_.info(f"Chose action {action}, returned message {message}")
            response = run_action(
                action=action,
                query=transcription,
                client=openai_client,
                config=config
            )
            log_.info(response)



if __name__ == "__main__":
    load_dotenv()

    with open("config.yaml", "r") as file:
        config = Box(yaml.safe_load(file))

    main(config=config)
