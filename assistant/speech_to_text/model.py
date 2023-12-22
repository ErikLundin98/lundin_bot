from box import Box
from queue import Queue
import numpy as np
import torch
import whisper
import time
import speech_recognition as sr


class Transcriber():
    """Transcriber class"""

    def __init__(self, config: Box):
        self.phrase_time = None
        self.data_queue = Queue()
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = config.speech_to_text.energy_threshold
        self.recorder.dynamic_energy_threshold = False
    
        self.source = sr.Microphone(device_index=0, sample_rate=16000)


        self.audio_model = whisper.load_model(config.speech_to_text.whisper_model)

        self.record_timeout = config.speech_to_text.record_timeout # how "real time" the recording is.
        self.transcription = ['']
        self.language = config.language

        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)

        def record_callback(_, audio: sr.AudioData) -> None:
            """
            Threaded callback function to receive audio data when recordings finish.
            audio: An AudioData containing the recorded bytes.
            """
            # Grab the raw bytes and push it into the thread safe queue.
            data = audio.get_raw_data()
            self.data_queue.put(data)

        self.recorder.listen_in_background(self.source, record_callback, phrase_time_limit=self.record_timeout)

    def get_transcription(self) -> str | None:
        if not self.data_queue.empty():
            audio_data = b''.join(self.data_queue.queue)
            self.data_queue.queue.clear()
            
            # Convert in-ram buffer to something the model can use directly without needing a temp file.
            # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
            # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Read the transcription.
            result = self.audio_model.transcribe(audio_np, fp16=torch.cuda.is_available(), language=self.language)
            text = result['text'].strip()
            return text
            
        time.sleep(0.25)    
        return None
            