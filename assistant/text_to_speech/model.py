from box import Box
import urllib.request 
import os
import logging
import tarfile
import subprocess

_log = logging.getLogger(__name__)

class TTS:
    def __init__(
        self,
        config: Box,
    ):
        """Initialize a Piper TTS model based on config."""
        (
            self.piper_bin_path, 
            self.piper_model_path
        ) = self._try_install_piper(config)

        _log.info("Initialized TTS model.")
    def _try_install_piper(self, config: Box):
        """Install piper if not already installed."""
        _log.info("Checking if piper exists.")
        local_install_path = os.path.join(
            os.getcwd(), 
            config.text_to_speech.binary_path,
        )
        if not os.path.exists(local_install_path):
            os.mkdir(local_install_path)

        piper_bin_path = os.path.join(
            local_install_path,
            "piper",
            "piper",
        )
        if not os.path.exists(piper_bin_path):
            tar_file_url = (
                config.text_to_speech.piper_tts_release_url +
                config.text_to_speech.binary_download_files[config.platform]
            )
            _log.info(f"Piper install not found, installing from {tar_file_url}...")
            tarfile_path = os.path.join(
                local_install_path, "piper.tar.gz"
            )
            urllib.request.urlretrieve(
                url=tar_file_url,
                filename=tarfile_path,
            )
            file = tarfile.open(tarfile_path)
            file.extractall(local_install_path)
            _log.info(f"Piper tts binary installed at {local_install_path}/piper")

        model_file_name = config.text_to_speech.piper_voice.model_file_name
        piper_model_path = os.path.join(
            local_install_path,
            model_file_name,
        )
        if not os.path.exists(piper_model_path):
            weights_url = config.text_to_speech.piper_voice.weights_url
            config_url = config.text_to_speech.piper_voice.config_url
            _log.info(f"Downloading model {model_file_name}.")
            _log.info(f"Weights url: {weights_url}")
            _log.info(f"Config url: {config_url}")
            urllib.request.urlretrieve(
                url=weights_url,
                filename=piper_model_path,
            )
            urllib.request.urlretrieve(
                url=config_url,
                filename=piper_model_path + ".json",
            )

            _log.info("Successfully downloaded model.")

        return piper_bin_path, piper_model_path
    
    def create_wav(
        self,
        text: str,
        filename: str = "voice",
    ) -> None:
        """Create tts wav file and save to disk."""
        echo_process = subprocess.Popen(
            ["echo", f"{text}"], 
            stdout=subprocess.PIPE, 
            text=True,
        )
        piper_command = [
            f"{self.piper_bin_path}",
            f"--model {self.piper_model_path}",
            f"--output_file {filename}.wav",
        ]
        piper_process = subprocess.Popen(
            piper_command,
            stdin=echo_process.stdout,
            stdout=subprocess.PIPE,
            text=True
        )

        output, error = piper_process.communicate()
        
        _log.info(output)
        _log.info(error)

if __name__ == "__main__":
    import yaml
    with open("config.yaml", "r") as file:
        config = Box(yaml.safe_load(file))

    tts = TTS(config)
    
    tts.create_wav(
        "Hej, detta är Erik som pratar!",
        "test"
    )