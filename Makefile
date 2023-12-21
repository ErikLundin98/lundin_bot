
all_mac:
	pip install -r assistant/speech_to_text/requirements.txt
	brew update 
	brew install ffmpeg
	brew install espeak

all_linux:
	pip install -r assistant/speech_to_text/requirements.txt
	sudo apt update
	sudo apt install ffmpeg
	sudo apt install espeak