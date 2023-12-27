from enum import Enum
import json

import os
from box import Box
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import logging

from assistant.language_model.model import LanguageModel
from assistant.language_model.utils import render_prompt

_log = logging.getLogger(__name__)

from assistant.constants import (
    AMPLIFIER_IP,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URL,
)


class MusicControlAction(Enum):
    """Contains all types of music control actions supported."""

    TURN_ON_AMP = "turn_on_amp"
    TURN_OFF_AMP = "turn_off_amp"
    LIST_PLAYLISTS = "list_playlists"
    PLAY_ITEM = "play_playlist"
    PAUSE = "pause"
    RESUME = "resume"
    PLAY = "play"
    VOLUME = "volume"
    HELP = "help"
    LIST_DEVICES = "list_devices"


class PlayType(Enum):
    TRACK = "track"
    ALBUM = "album"
    ARTIST = "artist"
    PLAYLIST = "playlist"
    SHOW = "show"
    EPISODE = "episode"
    AUDIOBOOK = "audiobook"


NAME = "music_control"


def main(
    query: str,
    llm: LanguageModel,
    config: Box,
) -> str:
    """Control music."""
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv(SPOTIFY_CLIENT_ID),
            client_secret=os.getenv(SPOTIFY_CLIENT_SECRET),
            redirect_uri=os.getenv(SPOTIFY_REDIRECT_URL),
            scope=[
                "user-library-read",
                "user-library-modify",
                "user-read-playback-state",
                "user-modify-playback-state",
                "user-read-currently-playing",
                "app-remote-control",
                "streaming",
            ],
        )
    )
    devices = sp.devices()["devices"]
    device_names = [device["name"] for device in devices]
    system_prompt = render_prompt(
        prompt_name=NAME,
        actions=", ".join(MusicControlAction.__members__),
        devices=", ".join(device_names),
        play_types=", ".join(PlayType.__members__),
        device_example=device_names[0],
    )
    answer = llm.answer_prompt(
        system_prompt=system_prompt,
        user_prompt=query,
    ).content
    try:
        answer_dict = json.loads(answer)
    except json.JSONDecodeError as e:
        _log.warning(f"Failed: {e}")
        return ""

    _log.info(f"Using params {answer_dict}")
    response = perform_music_action(
        sp=sp,
        action=answer_dict["action"],
        config=config,
        devices=devices,
        **answer_dict["args"],
    )
    return answer_dict["message"] + response


def perform_music_action(
    sp: spotipy.Spotify,
    action: MusicControlAction,
    config: Box,
    devices: list[str],
    **kwargs,
):
    """Perform music action."""
    selected_device_name = kwargs.get("device", None)
    if not selected_device_name:
        selected_device_name = config.smart_home.default_spotify_device.lower()
    device_id = next(
        device for device in devices if device["name"].lower() == selected_device_name.lower()
    )["id"]
    match action.lower():
        case MusicControlAction.TURN_ON_AMP.value:
            requests.get(f"http://{os.getenv(AMPLIFIER_IP)}/goform/formiPhoneAppDirect.xml?PWON")
        case MusicControlAction.TURN_OFF_AMP.value:
            requests.get(
                f"http://{os.getenv(AMPLIFIER_IP)}/goform/formiPhoneAppDirect.xml?PWSTANDBY"
            )
        case MusicControlAction.LIST_PLAYLISTS.value:
            return ", ".join(sp.current_user_playlists())
        case MusicControlAction.PLAY.value:
            play(
                sp=sp,
                play_type=kwargs.get("play_type"),
                query=kwargs.get("query"),
                device_id=device_id,
            )
        case MusicControlAction.PAUSE.value:
            sp.pause_playback(device_id=device_id)
        case MusicControlAction.RESUME.value:
            sp.start_playback(device_id=device_id)
        case MusicControlAction.VOLUME.value:
            sp.volume(**kwargs)
        case MusicControlAction.HELP.value:
            actions = ", ".join(MusicControlAction.__members__)
            return f"{actions}"
        case MusicControlAction.LIST_DEVICES.value:
            return ", ".join([device["name"] for device in devices])
        
    return ""


def play(sp: spotipy.Spotify, play_type: str, query: str, device_id: str):
    """Play any type of spotify media."""
    response = sp.search(query, type=play_type, limit=1)
    play_type_response = response.get(play_type + "s")
    first_item = play_type_response.get("items")[0]
    uri = first_item.get("uri")
    if play_type == PlayType.ALBUM.value:
        songs = [track["uri"] for track in sp.album(uri)["tracks"]["items"]]
    elif play_type == PlayType.PLAYLIST.value:
        songs = [track["track"]["uri"] for track in sp.playlist(uri)["tracks"]["items"]]
    elif play_type == PlayType.ARTIST.value:
        
        songs = [track["uri"] for track in sp.artist_top_tracks(uri)["tracks"]]
    else:
        songs = [uri]
    sp.start_playback(uris=songs, device_id=device_id)


# TODO make installation here easy for any device.
if __name__ == "__main__":
    from dotenv import load_dotenv
    import yaml

    with open("config.yaml", "r") as file:
        config = Box(yaml.safe_load(file))
    load_dotenv()
    response = perform_music_action(
        MusicControlAction.HELP,
        config=config,
    )
    print(response)
