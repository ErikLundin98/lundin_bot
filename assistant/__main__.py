import yaml
from box import Box
from assistant.language_model.tools import select_action
from assistant.speech_to_text.model import Transcriber
import time

from assistant.utils import contains_wake_word

def main(config: Box):
    """Start voice assistant service."""
    transcriber = Transcriber(config=config)
    language_model = ...
    print("Enter loop.")
    while True:
        transcription = transcriber.get_transcription()
        if transcription:
            print(transcription)
            if contains_wake_word(
                sentence=transcription,
                wake_word=config.speech_to_text.wake_word,
                threshold=config.speech_to_text.similarity_score
            ):
                print("is wake word")
        
                action = select_action.main(transcription)
                print(action)

if __name__ == "__main__":
    with open("config.yaml", "r") as file:
        config = Box(yaml.safe_load(file))
    main(config=config)

