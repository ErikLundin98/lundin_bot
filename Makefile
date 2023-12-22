
all_mac:
	pip install -r requirements.txt
	brew update 
	brew install ffmpeg
	brew install espeak

	make whisper_cpp # TODO replace with espeak-ng

all_linux:
	pip install -r requirements.txt
	sudo apt update
	sudo apt install ffmpeg
	sudo apt install espeak # TODO replace with espeak-ng

	make whisper_cpp

whisper_cpp:
	git submodule init && git submodule update
	cd whisper.cpp && make -j stream
	cd whisper.cpp && ./models/download-ggml-model.sh small

