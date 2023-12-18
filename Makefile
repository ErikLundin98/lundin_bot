speech_to_text:
	pip install -r assistant/speech_to_text/requirements.txt

speech_to_text_mac:
	speech_to_text
	brew install ffmpeg

speech_to_text_linux:
	speech_to_text
	sudo apt update && sudo apt install ffmpeg

all_mac:
	speech_to_text_mac

all_linux:
	speech_to_text_linux