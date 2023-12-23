# lundin_bot

Voice assistant

## Set up steps

First, update the config based on you requirements.

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

### Select tools

### Text to speech using piper tts

### OpenAI setup

### Control dirigera hub:

### Temp notes:

softwareupdate --install-rosetta

install_name_tool -change @rpath/libespeak-ng.1.dylib /Users/lundinerik/Prog/hobby/lundin_bot/lundin_bot/bin/piper/libespeak-ng.1.dylib /Users/lundinerik/Prog/hobby/lundin_bot/lundin_bot/bin/piper/piper

install_name_tool -change @rpath/libpiper_phonemize.1.dylib /Users/lundinerik/Prog/hobby/lundin_bot/lundin_bot/bin/piper/libpiper_phonemize.1.dylib /Users/lundinerik/Prog/hobby/lundin_bot/lundin_bot/bin/piper/piper

install_name_tool -change @rpath/libonnxruntime.1.14.1.dylib /Users/lundinerik/Prog/hobby/lundin_bot/lundin_bot/bin/piper/libonnxruntime.1.14.1.dylib /Users/lundinerik/Prog/hobby/lundin_bot/lundin_bot/bin/piper/piper





otool -l /Users/lundinerik/Prog/hobby/lundin_bot/lundin_bot/bin/piper/piper