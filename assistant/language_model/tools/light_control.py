
import json
import os
from assistant.constants import DIRIGERA_IP, DIRIGERA_TOKEN
from assistant.language_model.model import LanguageModel
from assistant.language_model.utils import render_prompt
from box import Box
import dirigera
from dirigera.devices.light import Light
import logging
import difflib

_log = logging.getLogger(__name__)
NAME = "light_control"

def main(
    query: str, 
    llm: LanguageModel,
    config: Box,
) -> str:
    """Control lights."""
    light_names = config.smart_home.dirigera.rooms
    system_prompt = render_prompt(
        prompt_name=NAME,
        light_names=", ".join(light_names),
        colors=", ".join([]) # TODO
    )
    answer = llm.answer_prompt(
        system_prompt=system_prompt,
        user_prompt=query,
        config=config,
    ).content
    try:
        answer_dict = json.loads(answer)
    except json.JSONDecodeError as e:
        _log.warning(f"Failed: {e}")
        return ""
    
    hub = dirigera.Hub(
        token=os.getenv(DIRIGERA_TOKEN),
        ip_address=os.getenv(DIRIGERA_IP)
    )
    _log.info(f"Using params {answer_dict}")
    perform_light_action(
        params=answer_dict,
        hub=hub,
        light_names=light_names,
    )

    return ""

def perform_light_action(
    params: dict,
    hub: dirigera.Hub,
    light_names: list[str],
):
    """Perform actions on lights specified by llm."""
    light_name = params.get("name", "")
    options = difflib.get_close_matches(light_name, light_names, cutoff=0.6)
    if options:
        light_name = options[0]
    lights = get_lights_matching_name(
        hub=hub,
        name=light_name,
    )
    for light in lights:
        if "color" in params:
            ...
        if "is_on" in params:
            light.set_light(lamp_on=params["is_on"])

def get_lights_matching_name(hub: dirigera.Hub, name: str) -> list[Light]:
    """Get all lights in room"""
    name = name.lower()
    return [
        light for light in hub.get_lights()
        if light.room.name.lower() == name
        or any(device_set["name"].lower() == name for device_set in light.device_set)
        or light.attributes.custom_name.lower() == name
    ]