# lundin_bot

**NOTE**: This project is still in WIP

A simple voice assistant bot built for running on a Raspberry Pi 4 or above using
* [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) for speech-to-text
* [ChatGPT](https://github.com/openai/openai-python) for doing as the user wishes
* [Piper](https://github.com/rhasspy/piper) for text-to-speech.
  * I have trained the Piper TTS (VITS based) model on my own voice. By default, this is the voice used for the assistant.

This is a hobby project intended for personal use.
You are welcome to use the project for your own purposes as well.

Current capabilities are:

- Random Q&A (limited by LLM capabilities)
- Get weather forecasts & synthetsize to user based on their query
- Control lights in the home
- Control music & music devices in the home.

## TODO

* Improve installation
* Make sure works on linux
* Fix enabling/disabling of actions
* Add memory + conversational capabilities
* Trim performance for raspberry pi (config params)
* Fix tutorial and code for first time usage of spotify app.
* Potentially optimize performance by disabling whisper when not needed.

## Limitations

Right now, the project is heavily personalized for my smart devices in my home and will likely not work out of the box with yours:

* I use IKEA's [Dirigera](https://www.ikea.com/se/sv/p/dirigera-hubb-foer-smarta-produkter-vit-smart-10503406/) devices
* I use a Denon CEOL piccolo Amp for my music needs. Turning on and off the amp using the voice assistant is hardcoded to work with this device only (see [music_control.py](/assistant/language_model/tools/music_control.py)) for details
* Weather lookup supports SMHI (Sweden Meterological Institute):s API, and is therefore limited to Swedish data.
If you do not have these devices at home, I recommend disabling these two tools.

## Installation

* You need a OpenAI api key to use the assistant (alternatively, you can alter the [llm model code](/assistant/language_model/model.py) to use another model)
* You need to create a Spotify API application on the [Spotify developer portal](https://developer.spotify.com/dashboard)

First, update the config based on your requirements.

NOTE: Python version needs to be between 3.7 and 3.10.

Mac: 
```bash
python3 -m venv venv
source venv/bin/activate
make install_mac
```

Linux: 
```bash
python3 -m venv venv
source venv/bin/activate
make install_linux
```

Then, make sure to set the following environment variables:

* `OPENAI_API_KEY`
* `OPENAI_ORGANIZATION`
* `DIRIGERA_IP`
* `DIRIGERA_TOKEN`
* `SPOTIFY_WEB_PLAYBACK_ACCESS_TOKEN`
* `SPOTIFY_CLIENT_ID`
* `SPOTIFY_CLIENT_SECRET`
* `SPOTIFY_REDIRECT_URL` (can be set to http://google.com/callback/)
* `AMPLIFIER_IP`
* `HOME_LAT`
* `HOME_LON`

## Running the assistant

When this is done, simply run 
```python3
python -m assistant
```

**NOTE**: If running on an M1 mac, after running the model for the first time, the TTS module might crash due to missing dependencies. If this happens, there is a patch available which can be run by running
```bash
make fix_piper_tts_mac
```