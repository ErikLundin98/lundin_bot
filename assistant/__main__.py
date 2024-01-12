import os
import signal
from dotenv import load_dotenv
import yaml
from box import Box
from assistant.language_model.action import run_action
from assistant.language_model.model import LanguageModel
from assistant.language_model.tools import select_action
from assistant.speech_to_text.model import Transcriber
import logging
from assistant.text_to_speech.model import TTS
from assistant.utils import contains_wake_word

log_ = logging.getLogger(__name__)

def main(config: Box):
    """Start voice assistant service."""
    transcriber = Transcriber(config=config)
    llm = LanguageModel(config=config)
    tts = TTS(config=config)
    log_.info("Initialized transcriber, llm client.")
    try:
        for transcription in transcriber.start():
            try:
                handle_transcription(transcription=transcription, llm=llm, tts=tts)
            except Exception as e:
                log_.warning(f"An exception occurred when handling transcription: {e}")
    except KeyboardInterrupt:
        log_.info("Stopping assistant loop.")
        raise KeyboardInterrupt()

def handle_transcription(transcription:str, llm:LanguageModel, tts: TTS):
    """Handle transcription."""

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
                llm=llm,
                config=config
            )
            log_.info(f"Chose action {action}, returned message {message}")
            tts.stream_audio(text=message, config=config)
            response = run_action(
                action=action,
                query=transcription,
                llm=llm,
                config=config
            )
            tts.stream_audio(text=response, config=config)
            log_.info(response)



if __name__ == "__main__":
    pg_id = os.getpgrp()
    load_dotenv()

    with open("config.yaml", "r") as file:
        config = Box(yaml.safe_load(file))
    try:
        main(config=config)
    except Exception as e:
        log_.warning("Exception while running voice assistant:")
        log_.warning(e)
    finally:
        os.killpg(pg_id, signal.SIGKILL)
