import json
from multiprocessing import freeze_support
import os

from trainer import Trainer, TrainerArgs

from TTS.tts.configs.shared_configs import BaseDatasetConfig
from TTS.tts.configs.vits_config import VitsConfig, VitsArgs
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models.vits import Vits, VitsAudioConfig
from TTS.tts.utils.text.tokenizer import TTSTokenizer
from TTS.utils.audio import AudioProcessor
import torch

config_dict = { 
    "model_args": VitsArgs(**{
        "num_chars": 137,
        "out_channels": 513,
        "spec_segment_size": 32,
        "hidden_channels": 192,
        "hidden_channels_ffn_text_encoder": 768,
        "num_heads_text_encoder": 2,
        "num_layers_text_encoder": 6,
        "kernel_size_text_encoder": 3,
        "dropout_p_text_encoder": 0.1,
        "dropout_p_duration_predictor": 0.5,
        "kernel_size_posterior_encoder": 5,
        "dilation_rate_posterior_encoder": 1,
        "num_layers_posterior_encoder": 16,
        "kernel_size_flow": 5,
        "dilation_rate_flow": 1,
        "num_layers_flow": 4,
        "resblock_type_decoder": "2",
        "resblock_kernel_sizes_decoder": [
            3,
            5,
            7
        ],
        "resblock_dilation_sizes_decoder": [
            [
                1,
                2
            ],
            [
                2,
                6
            ],
            [
                3,
                12
            ]
        ],
        "upsample_rates_decoder": [
            8,
            8,
            4
        ],
        "upsample_initial_channel_decoder": 256,
        "upsample_kernel_sizes_decoder": [
            16,
            16,
            8
        ],
        "periods_multi_period_discriminator": [
            2,
            3,
            5,
            7,
            11
        ],
        "use_sdp": True,
        "noise_scale": 1.0,
        "inference_noise_scale": 0.3,
        "length_scale": 1.0,
        "noise_scale_dp": 1.0,
        "inference_noise_scale_dp": 0.3,
        "init_discriminator": True,
        "use_spectral_norm_disriminator": False,
        "use_speaker_embedding": True,
        "num_speakers": 0,
        "speakers_file": "/Users/lundinerik/Library/Application Support/tts/tts_models--sv--cv--vits/speaker_ids.json",
        "speaker_embedding_channels": 256,
        "use_d_vector_file": False,
        "d_vector_dim": 0,
        "detach_dp_input": True,
        "use_language_embedding": True,
        "embedded_language_dim": 4,
        "num_languages": 1,
        "use_speaker_encoder_as_loss": False,
        "speaker_encoder_config_path": "",
        "speaker_encoder_model_path": "",
        "condition_dp_on_speaker": True,
        "freeze_encoder": False,
        "freeze_DP": False,
        "freeze_PE": False,
        "freeze_flow_decoder": False,
        "freeze_waveform_decoder": False,
        "interpolate_z": True,
        "reinit_DP": False,
        "reinit_text_encoder": False
    }),
}

def ljspeech_formatter(
    root_path, meta_file, **kwargs
):  # pylint: disable=unused-argument
    """Normalizes the LJSpeech meta data file to TTS format
    https://keithito.com/LJ-Speech-Dataset/"""
    txt_file = os.path.join(root_path, meta_file)
    items = []
    speaker_name = "ljspeech"
    with open(txt_file, "r", encoding="utf-8") as ttf:
        for line in ttf:
            cols = line.split("|")
            wav_file = os.path.join(root_path, "wav", cols[0])
            text = cols[1]
            items.append(
                {
                    "text": text,
                    "audio_file": wav_file,
                    "speaker_name": speaker_name,
                    "root_path": root_path,
                }
            )
    return items


def main():
    output_path = "data/output/"
    dataset_config = BaseDatasetConfig(
        formatter="ljspeech", meta_file_train="metadata.csv", path="../output_dataset/"
    )
    audio_config = VitsAudioConfig(
        sample_rate=22050,
        win_length=1024,
        hop_length=256,
        num_mels=80,
        mel_fmin=0,
        mel_fmax=None,
    )

    config = VitsConfig(
        audio=audio_config,
        run_name="vits_ljspeech",
        batch_size=32,
        eval_batch_size=16,
        batch_group_size=5,
        num_loader_workers=8,
        num_eval_loader_workers=4,
        run_eval=True,
        test_delay_epochs=-1,
        epochs=1000,
        use_phonemes=True,
        phoneme_language="sv",
        phoneme_cache_path=os.path.join(output_path, "phoneme_cache"),
        compute_input_seq_cache=True,
        print_step=25,
        print_eval=True,
        mixed_precision=True,
        output_path=output_path,
        datasets=[dataset_config],
        cudnn_benchmark=False,
    )
    config.update(config_dict)

    # breakpoint()
    # INITIALIZE THE AUDIO PROCESSOR
    # Audio processor is used for feature extraction and audio I/O.
    # It mainly serves to the dataloader and the training loggers.
    ap = AudioProcessor.init_from_config(config)

    # INITIALIZE THE TOKENIZER
    # Tokenizer is used to convert text to sequences of token IDs.
    # config is updated with the default characters if not defined in the config.
    tokenizer, config = TTSTokenizer.init_from_config(config)

    # LOAD DATA SAMPLES
    # Each sample is a list of ```[text, audio_file_path, speaker_name]```
    # You can define your custom sample loader returning the list of samples.
    # Or define your custom formatter and pass it to the `load_tts_samples`.
    # Check `TTS.tts.datasets.load_tts_samples` for more details.

    train_samples, eval_samples = load_tts_samples(
        dataset_config,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
        formatter=ljspeech_formatter,
    )

    # init model
    model = Vits(config, ap, tokenizer, speaker_manager=None)

    # init the trainer and 🚀
    trainer = Trainer(
        TrainerArgs(
            restore_path="/Users/lundinerik/Library/Application Support/tts/tts_models--sv--cv--vits/model_file.pth.tar",
        ),
        config,
        output_path,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )
    trainer.fit()


if __name__ == "__main__":
    freeze_support()
    main()
