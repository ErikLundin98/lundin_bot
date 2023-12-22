from typing import Generator
from box import Box
import subprocess
import os
import logging

_log = logging.getLogger(__name__)

class Transcriber:
    """Simple Whisper CPP model wrapper."""

    TRANSCRIPTION_FILE_PATH = "..data/transcription.txt"
    def __init__(self, config: Box):
        """Initialize Whisper CPP model."""
        cpp_config = config.speech_to_text.whisper_cpp
        self.length = cpp_config.length
        self.capture_device = cpp_config.capture_device
        self.n_threads = cpp_config.n_threads
        self.audio_context_len = cpp_config.audio_context_len
        self.vad_thold = cpp_config.vad_thold
        self.file_path = cpp_config.file_path
        self.last_transcription = None

    def start(self) -> Generator[str | None, None, None]:
        """Start transcription in subprocess, return transcriptions as generator."""
        stream_cmd = [
            "./stream",
            "-m", "models/ggml-small.bin",
            "--step", "0",
            "--language", "swedish",
            "--length", f"{self.length}",
            "--capture", f"{self.capture_device}",
            "--threads", f"{self.n_threads}",
            "--audio-ctx", f"{self.audio_context_len}", 
            "--vad-thold", f"{self.vad_thold}",
            "--file", f"{self.file_path}", # TODO remove?
            "--save-audio",
            # "--keep", '0'
        ]
        _log.info(f"Running command {' '.join(stream_cmd)}")

        log_file = open("data/transcription_error_log.txt", "a")
        self._p = subprocess.Popen(
            args=stream_cmd,
            cwd=os.path.join(os.getcwd(), "whisper.cpp"),
            stdout=subprocess.PIPE,
            stderr=log_file,
            shell=False,
            encoding="utf8"
        )
        for line in iter(self._p.stdout.readline, ""):
            if line[0] == "[":
                self.last_transcription = line.split("]")[-1].strip()
            if "###" in line and "END" in line:
                _log.info(f"Got sentence {self.last_transcription}")
                yield self.last_transcription
            yield None


if __name__ == "__main__":
    import signal
    import yaml
    pg_id = os.getpgrp()
    with open("config.yaml", "r") as file:
        config = Box(yaml.safe_load(file))
        
    model = Transcriber(config)
    try:
        for line in model.start_transcribing():
            print(line)
    
    finally:
        os.killpg(pg_id, signal.SIGKILL)